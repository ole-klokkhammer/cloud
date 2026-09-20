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
      -> python: YOLO26 (torch, CUDA) at 640x640 letterbox
      -> per-burst BEST-FRAME selection (confidence x area score, ring of 16)
      -> stills: /detections/events/cat_YYYYMMDD_HHMMSS.jpg   (embedder picks these up)
      -> one NATS event per burst: subject surveillance.detector
         (any consumer: alerts, query agent, ...; the embedder still polls the dir)

two features carried over from the .NET version (ported 1:1):

- **best-frame storage** - within a detection burst, every inferred frame is
  scored `confidence x target_area_fraction`; the highest-scoring frame of the
  burst is the one stored (the clearest/closest cat view), not an arbitrary
  frame on a timer.
- **events** - one JSON event per burst (detection dedupe), logged to the
  journal AND published to NATS (`surveillance.detector`).

