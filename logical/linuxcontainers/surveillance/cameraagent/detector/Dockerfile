FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /app
COPY /app/ /app/
RUN dotnet publish /app/detector.csproj -c Release -r linux-x64 --self-contained true -o /app/publish

# libonnxruntime_providers_cuda.so (from the ORT-GPU nuget) links libcublas*/libcudnn*
# sonames but the nuget does NOT carry cuBLAS/cuDNN. Vendor the CUDA 13 runtime libs
# (sm_120-capable) - same major as the torch cu130 wheels, host driver 13.3 covers it.
FROM docker.io/nvidia/cuda:13.0.3-cudnn-runtime-ubuntu24.04 AS cuda

FROM mcr.microsoft.com/dotnet/aspnet:8.0

ENV LD_LIBRARY_PATH=/usr/local/cuda/lib64
# single glob: cuBLAS, cuBLASLt, cuDNN (+split engines), cuFFT, cuRAND, NPP, NVRTC
COPY --from=cuda /usr/local/cuda/lib64/lib*so* /usr/local/cuda/lib64/

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    ffmpeg libgomp1 tzdata \
    && rm -rf /var/lib/apt/lists/*

COPY --from=build /app/publish .

ENTRYPOINT ["dotnet", "detector.dll"]
