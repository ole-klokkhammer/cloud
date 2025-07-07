FROM python:3.13.5-slim

WORKDIR /app 

# Install dependencies for OpenCV and FFmpeg with HEVC (libx265) support
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ffmpeg \
        libsm6 \
        libxext6 \
        libx265-dev \
        libopencv-dev \
        python3-opencv \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /app/requirements.txt 
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt


COPY ./app /app/app 

CMD ["python", "app/main.py"]
