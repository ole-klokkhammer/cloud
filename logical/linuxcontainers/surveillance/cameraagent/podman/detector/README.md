# detector - camera object detection (cats), python/torch + CUDA

GPU YOLO service running in the **cameraagent LXC** (`core:cameraagent`;
mediamtx runs in its own LXC). Written in **python (torch + ultralytics)**:
inference runs on the RTX 5060 Ti via the torch CUDA build - the torch wheel
bundles its own CUDA runtime, so the container only needs the **driver**
(CDI `AddDevice=nvidia.com/gpu=all`); no nvidia/cuda base, no /opt/cuda-runtime
mount, no ONNX export. (The .NET/ONNX attempt lives on in `app-csharp/` as a
reference - it needed host-side CUDA runtime plumbing this LXC lacks.)

## what it does

    camera -> mediamtx (:8554, substream) -> OpenCV RTSP capture
      -> python: YOLO11 (torch, CUDA) at 640x640 letterbox
      -> per-burst BEST-FRAME selection (confidence x area score, ring of 16)
      -> stills: /detections/events/cat_YYYYMMDD_HHMMSS.jpg   (embedder picks these up)
      -> one NATS event per burst: subject surveillance.detector
         (any consumer: alerts, query agent, ...; the embedder still polls the dir)

two features carried over from the .NET version (ported 1:1):

* **best-frame storage** - within a detection burst, every inferred frame is
  scored `confidence x target_area_fraction`; the highest-scoring frame of the
  burst is the one stored (the clearest/closest cat view), not an arbitrary
  frame on a timer.
* **events** - one JSON event per burst (detection dedupe), logged to the
  journal AND published to NATS (`surveillance.detector`).

## model

plain **yolo11m.pt** (stock COCO; ~40 MB) - no export step at all:
training/fine-tuning and serving now share one language and one artifact.
The model is NOT in the image: `make push-model` ships it into the LXC's
`/models` (= PVE `/ssd/llm/models/detector`, mounted read-only in the
quadlet), so model swaps never rebuild the image:

    # one-off: get the checkpoint into this folder (already on core from the
    # .NET era - detector/yolo11m.pt)
    # fine-tune: label stills, `yolo detect train ...`, drop the trained
    # .pt in this folder, `make push-model`, point DETECTOR_MODEL at it

## layout

    podman/detector/
      app/
        detector.py          the whole service (~250 lines: capture, inference,
                             best-frame ring, stills, NATS burst events)
        requirements.txt     torch + ultralytics + opencv-headless + nats-py
      app-csharp/            the .NET/ONNX reference implementation (superseded)
      yolo11m.pt             model checkpoint (gitignored; 'make push-model' ships it)
      Dockerfile             python:3.12-slim base + pip torch (CUDA wheels ~8 GB)
      detector.container     podman quadlet (Network=host, CDI GPU,
                             /detections rw + /models ro, per profile.yaml)
      detector.env.example   copy to LXC /env/surveillance/detector.env
      Makefile               push-model / image (build in LXC) / deploy / logs

## LXC preflight (run once)

    lxc exec core:cameraagent -- sh -c '
      nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv
      systemctl is-active nvidia-cdi-refresh.service
      df -h /var/lib/containers /detections /models'

* NVIDIA driver visible in the LXC + CDI running (`AddDevice=nvidia.com/gpu=all`)
* ~10 GB free in /var/lib/containers (torch + nvidia runtime wheels ~8 GB)
* the torch wheels bundle cuBLAS/cuDNN/cudart - the LXC driver
  (13.3-capable) is forward-compatible; sm_120 (RTX 5060 Ti/5090) is covered
  by recent torch CUDA wheels (>= 2.7)
* the build runs `pip install` inside the LXC - the LXC needs pypi.org
  reachability (same as the old detectorpy/ embedder builds)

## deploy

    cd logical/linuxcontainers/surveillance/cameraagent/podman/detector
    make push-model      # ship yolo11m.pt into the LXC /models (mounted ro)
    make image           # ON THE LXC: podman build (context = this dir)
    make deploy          # ON CORE: quadlet + restart
    make logs

expected log lines:

    [detector] watching rtsp://mediamtx.homelan:8554/entrance_roof_sub (classes: 15)
    [detector] device: cuda (torch 2.x, cuda 13.x)
    [detector] model ready: /models/yolo11m.pt (input 640x640)
    [detector] stream 1280x720 (stills <= 1280px wide)
    [detector] nats connected: nats://nats.homelan:4222
    [detector] capture started (1280x720 bgr frames)
    [detector] {"event":"detection","camera":"entrance_roof","ts":"...","dets":1,"best_conf":0.63,"bbox":[...]}
    [detector] best still stored: /detections/events/cat_20260918_143520.jpg (burst of 17 detection frames, best conf 0.87)
    [detector] {"event":"detection_burst","camera":"entrance_roof","label":"cat","detections":17,
                "best":{"file":"cat_...jpg","path":"/detections/events/cat_...jpg",
                "confidence":0.87,"frame_ts":"...","box":[...]},"detector":"detector.py/1.0"}
    [detector] {"event":"heartbeat","frames":600,"fps":9.8,"last_dets":0,"stream_ok":true}

the `detection_burst` line is also published to NATS subject `surveillance.detector`.

## config (env, /env/surveillance/detector.env)

    DETECTOR_RTSP_URL          rtsp://mediamtx.homelan:8554/entrance_roof_sub
    DETECTOR_MODEL             /models/yolo11m.pt          (mounted ro; override = fine-tuned .pt)
    DETECTOR_CLASS             15                          COCO ids, comma-separated
    DETECTOR_FRAME_WIDTH       1280                        stills wider than this get downscaled
    DETECTOR_INPUT_SIZE        640                         yolo inference input
    DETECTOR_MIN_CONF          0.5                         runtime floor (NMS iou 0.45 fixed in code)
    DETECTOR_MAX_FPS           10                          inference throttle
    DETECTOR_BURST_WINDOW_SECS 2.0                         burst close timeout
    DETECTOR_EVENT_DIR         /detections/events
    DETECTOR_CAMERA            entrance_roof
    DETECTOR_DEVICE            cuda                        (or cpu to test without the GPU)
    NATS_URL                   nats://nats.homelan:4222
    NATS_SUBJECT               surveillance.detector

## events

* one `detection_burst` per burst (a burst = detections within
  `DETECTOR_BURST_WINDOW_SECS` of each other) - deduped, not per-frame
* stills are the source of truth: if NATS is down, stills are still stored
  and the embedder is unaffected; events resume when the bus is back
* the embedder keeps polling the stills dir - a NATS-triggered embedder
  is a later option if the poll lag ever matters

## ops

    make logs
    lxc exec core:cameraagent -- journalctl -u detector --since today | grep -c detection_burst
    lxc exec core:cameraagent -- du -sh /detections/events

## notes

* cpu fallback: `DETECTOR_DEVICE=cpu` (and automatic - if CUDA init fails at
  startup the service logs it and keeps running on CPU, it no longer crash-loops)
* TensorRT: ultralytics can export the .pt to a TRT engine later
  (`yolo export format=engine`); the plain CUDA path is the safe default
* the embedder/query folders in `../` are unchanged - same stills dir
  contract (`/detections/events`), same NATS subject
