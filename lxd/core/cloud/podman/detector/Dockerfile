# RTSP consumer + event publisher only: inference runs in the triton
# container (surveillance/triton, onnxruntime backend), reached over
# gRPC on 127.0.0.1:8001 (both host-network in the camagent LXC). The
# letterbox + NMS live in this process (triton_client.py); no torch,
# no GPU device here.
#
# ffmpeg is here too: the live-push (H.264 RTSP annotated re-stream
# into mediaMTX) shells out to it.
FROM docker.io/library/python:3.13-slim

# opencv's manylinux wheel bundles FFmpeg (the RTSP capture backend) but
# still needs system glib. Bookworm and trixie name the package
# differently (t64 suffix), so try both. ffmpeg (the live-push
# encoder) rides in the same apt run.
RUN apt-get update \
 && apt-get install -y --no-install-recommends ffmpeg \
 && (apt-get install -y --no-install-recommends libglib2.0-0 \
     || apt-get install -y --no-install-recommends libglib2.0-0t64) \
 && rm -rf /var/lib/apt/lists/*

COPY app/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --break-system-packages -r /tmp/requirements.txt

COPY app /app

WORKDIR /app

ENTRYPOINT ["python"]
CMD ["/app/main.py"]
