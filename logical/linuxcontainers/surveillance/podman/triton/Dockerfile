FROM nvcr.io/nvidia/tritonserver:25.08-py3

COPY model_repository /model_repository

# 8000 = HTTP (debug / curl health), 8001 = gRPC (the detector's client),
# 8005 = metrics
EXPOSE 8000 8001 8005
