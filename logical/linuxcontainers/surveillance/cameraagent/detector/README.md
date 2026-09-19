# detector - camera object detection (cats), .NET + ONNX Runtime GPU

GPU YOLO service running in the **cameraagent LXC** (`core:cameraagent`;
mediamtx runs in its own LXC). Written in **.NET 8 / C#**, infers with
**ONNX Runtime (CUDA execution provider)** on the RTX 5060 Ti.

the python version lives on in `../detector-python/` (unit `detectorpy`)
as a fallback; delete it once this one is proven.

## what it does

    camera -> mediamtx (:8554, substream) -> ffmpeg raw-BGR pipe
      -> C# : bilinear downscale + letterbox -> ONNX YOLO11 (CUDA)
      -> per-burst BEST-FRAME selection (confidence x area score)
      -> stills: /detector/events/cat_YYYYMMDD_HHMMSS.jpg   (embedder picks these up)
      -> one NATS event per burst: subject surveillance.detector
         (any consumer: alerts, query agent, ...; the embedder still polls the dir)

two features the python version didn't have:

* **best-frame storage** - within a detection burst, every inferred frame is
  scored `confidence x target_area_fraction`; the highest-scoring frame of the
  burst is the one stored (the clearest/closest cat view), not an arbitrary
  frame on a timer.
* **events** - one JSON event per burst (detection dedupe), logged to the
  journal AND published to NATS (`surveillance.detector`).

## model

the service runs an **exported ONNX** (not the raw .pt - .NET has no
ultralytics; training/fine-tuning stays a python job). export once:

    yolo export model=yolo11m.pt format=onnx imgsz=640 nms=True conf=0.5 iou=0.45

(on any machine with ultralytics; CPU is fine, ~2 min). `nms=True` bakes
NMS + the conf floor + max_det into the graph: output is `[1, 300, 6]` =
`x1 y1 x2 y2 score class` (best-first, zero-score padding rows), so C#
post-processing is trivial. put the resulting `yolo11m.onnx` in this
folder - the image does NOT contain the model: `make push-model` ships
it into the LXC (`lxc file push` to `/models`, mounted read-only in the
quadlet), so model swaps never rebuild the image.

the one in this folder is the stock yolo11m (COCO) export of 2026-09-19
(conf=0.5, iou=0.45 baked in; ~77 MB, gitignored).

fine-tune later the same way as before: label stills,
`yolo detect train ...`, export the fine-tuned model to .onnx, drop the
`.onnx` into this folder, `cd podman && make push-model` (ships it to the
LXC's `/models/`, no image rebuild), point `DETECTOR_MODEL` at
`/models/<file>.onnx` in `/env/surveillance/detector.env`.

TensorRT: the ORT GPU nuget also ships the TensorRT provider. one line
in `app/YoloModel.cs` (`options.AppendExecutionProvider_Tensorrt(new
OrtTensorRTProviderOptions { ... })`) switches to it; verify the ORT release's
bundled TRT supports sm_120 (consumer Blackwell, TRT 10.3-generation). the
plain CUDA provider used now is the safe default.

## layout

    detector/
      app/                     the C# service (one project, files by responsibility)
        detector.csproj        net8.0; ORT-GPU + nats.net + ImageSharp
        Program.cs             entry point: config wiring + main loop
        Config.cs              env-var config (DetectorOptions)
        Capture.cs             ffprobe + ffmpeg raw BGR24 pipe
        YoloModel.cs           ONNX session + letterbox/resize + inference
        BurstState.cs          candidate ring + best-frame selection
        StillStore.cs          JPEG stills
        NatsBus.cs             NATS connect/reconnect/publish + event payload
        Log.cs Labels.cs       logging + COCO class labels
      yolo11m.onnx             exported model (exported artifact, not in git)
      yolo11m.pt               upstream checkpoint (for re-export / fine-tune)
      podman/
        Dockerfile             two-stage: restore-layered SDK build -> self-contained
                              publish on any glibc base (BASE_SDK/BASE_RT build args;
                              the locked LXC pulls bases from registry.linole.org)
        detector.container     podman quadlet (Network=host, CDI GPU,
                               /media rw, /models + /config/detector ro)
        detector.env.example   copy to LXC /env/surveillance/detector.env
        Makefile               push-model / image (build in LXC) / deploy / logs

## LXC preflight (run once)

    lxc exec core:camagent -- sh -c '
      nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv
      systemctl is-active nvidia-cdi-refresh.service
      df -h /var/lib/containers /media'

* NVIDIA driver visible in the LXC + CDI running (`AddDevice=nvidia.com/gpu=all`)
* ~1.5 GB free in /var/lib/containers for the image (~0.8 GB build output; vs ~10 GB for the python torch one)
* the ORT GPU nuget bundles its CUDA runtime; the LXC driver (13.3-capable)
  is forward-compatible with it, exactly like the old torch-wheels story
* the build pulls `mcr.microsoft.com/dotnet/sdk:8.0` (~1.3 GB) and the
  ORT GPU package (~1.5 GB) inside the LXC - the LXC needs nuget.org reachability

## deploy

    cd logical/linuxcontainers/surveillance/cameraagent/detector
    # model: yolo11m.onnx must be in this folder (see "model")
    cd podman
    make push-model      # ship yolo11m.onnx into the LXC (/models, mounted ro in the quadlet)
    make image           # build in the LXC - bases from your registry:
    #   make image BASE_SDK=registry.linole.org/<sdk-image> BASE_RT=registry.linole.org/<glibc-base>
    #   (defaults: registry.linole.org/dotnet-sdk:8.0 + debian-bookworm-slim;
    #   if you haven't put those on your registry, push them first (skopeo, Dockerfile header))
    make deploy          # quadlet + env + restart
    make logs

expected log lines:

    [detector] watching rtsp://mediamtx.homelan:8554/entrance_roof_sub (classes: 15)
    [detector] device: cuda (onnx runtime CUDA execution provider)
    [detector] model ready: /models/yolo11m.onnx (input 'images', 640x640)
    [detector] stream 2560x1440 -> decode 1280x720 (stills at this res)
    [detector] nats connected: nats://127.0.0.1:4222
    [detector] ffmpeg decode started (1280x720 bgr24 raw pipe)
    {"event":"detection","camera":"entrance_roof","ts":"...","dets":1,"best_conf":0.63,"bbox":[...]}
    [detector] best still stored: /detector/events/cat_20260918_143520.jpg (burst of 17 detection frames, best conf 0.87)
    {"event":"detection_burst","camera":"entrance_roof","label":"cat","detections":17,
     "best":{"file":"cat_20260918_143520.jpg","path":"/detector/events/cat_20260918_143520.jpg",
             "confidence":0.87,"frame_ts":"...","box":[x1,y1,x2,y2]},"detector":"detector.net/1.0"}
    {"event":"heartbeat","frames":600,"fps":9.8,"last_dets":0,"stream_ok":true}

the `detection_burst` line is also published to NATS subject `surveillance.detector`.

## config (env, /env/surveillance/detector.env)

    DETECTOR_RTSP_URL          rtsp://mediamtx.homelan:8554/entrance_roof_sub
    DETECTOR_MODEL             /models/yolo11m.onnx        baked; override w/ /config/detector/*.onnx
    DETECTOR_CLASS             15                          COCO ids, comma-separated
    DETECTOR_FRAME_WIDTH       1280                        decode width = still resolution
    DETECTOR_INPUT_SIZE        640                         ONNX input (must match export imgsz)
    DETECTOR_MIN_CONF          0.5                         runtime floor
    DETECTOR_MAX_FPS           10                          inference throttle
    DETECTOR_BURST_WINDOW_SECS 2.0                         burst close timeout
    DETECTOR_EVENT_DIR         /detector/events
    DETECTOR_CAMERA            entrance_roof
    DETECTOR_DEVICE            cuda                        (or cpu to test without the GPU)
    NATS_URL                   nats://127.0.0.1:4222
    NATS_SUBJECT               surveillance.detector

## events

* one `detection_burst` per burst (a burst = detections within
  `DETECTOR_BURST_WINDOW_SECS` of each other) - deduped, not per-frame
* stills are the source of truth: if NATS is down, stills are still stored
  and the embedder is unaffected; events resume when the bus is back
* the embedder keeps polling `/detector/events` - a NATS-triggered embedder
  is a later option if the 5s poll lag ever matters

## ops

    make logs
    lxc exec core:camagent -- journalctl -u detector --since today | grep detection_burst | wc -l
    lxc exec core:camagent -- du -sh /detector/events

## rollback

the python detector still builds: `cd ../detector-python/podman && make image deploy`
(unit `detectorpy`, env `/env/surveillance/detectorpy.env`).
both units can run side by side (separate images/env files); stop one before
the other writes stills for the same camera to avoid duplicate embeddings.
