# The default AMD64 GPU image uses PyTorch 2.14 and CUDA 13.2. On Linux, CDI device requests require Docker >= 28.2.0 and NVIDIA Container Toolkit >= 1.18; 
# the legacy --gpus all flag can lose GPU access after host daemon reloads, so use --device instead. 
# See the Docker Quickstart Guide for the full image table (CPU, export, ARM64, and JetPack variants), host driver requirements, and volume mounts.
FROM docker.io/ultralytics/ultralytics:latest

COPY app /app

RUN pip install --no-cache-dir --break-system-packages -r /app/requirements.txt 

WORKDIR /app

CMD ["python", "-c", "/app/main.py"]
