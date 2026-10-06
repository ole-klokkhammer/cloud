# Minimal system libs (python:slim ships none of these):
#   libgomp1     OpenMP runtime - hard requirement: `import torch` links
#                against system libgomp.so.1; without it the base
#                payload itself crashes at import
#   libglib2.0-0 GLib - opencv-python-headless still links libglib-2.0
#                ("headless" = no X11, not no-GLib). Kept in the base:
#                any future py312 consumer doing vision needs it
#   tzdata       zoneinfo database - no crash mode, but without it
#                TZ=Europe/Oslo is inert and ZoneInfo falls back to UTC
#                with a warning. Cheapest alternative if ever dropped:
#                a `pip install tzdata` (pure-python wheel) instead
# The CUDA runtime itself is NOT apt: it arrives as nvidia-* pip wheels
# from the index-url below; host PVE only provides driver + CDI node.

FROM docker.io/python:3.12-slim
 
ARG WHEEL_CHANNEL=cu130
ENV WHEEL_CHANNEL=$WHEEL_CHANNEL
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 libglib2.0-0 tzdata \
    && rm -rf /var/lib/apt/lists/*
    
RUN pip install --break-system-packages --no-cache-dir \
      --index-url https://download.pytorch.org/whl/${WHEEL_CHANNEL} \
      torch torchvision