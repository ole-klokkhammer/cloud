# RTSP consumer + event publisher only: inference runs in the triton
# container, reached over gRPC at $TRITON_URL (apps.network); no torch,
# no GPU device here (letterbox + NMS live in triton_client.py).
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

# The code mixes three import styles (app.services.*, services.*, config.*),
# so BOTH the package and its parent must be on sys.path. -m puts the
# parent there; PYTHONPATH adds the package dir. (The clean fix is making
# every import app.-qualified; this is the honest minimum.)
COPY app /srv/detector/app
ENV PYTHONPATH=/srv/detector/app

WORKDIR /srv/detector

ENTRYPOINT ["python"]
CMD ["-m", "app.main"]
