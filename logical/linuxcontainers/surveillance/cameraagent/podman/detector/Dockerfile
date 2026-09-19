FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /app
COPY app/ /app/
RUN dotnet publish /app/detector.csproj -c Release -r linux-x64 --self-contained true -o /app/publish

FROM docker.io/nvidia/cuda:13.0.3-cudnn-runtime-ubuntu24.04
# pull .NET 8 runtime onto the cuda base
COPY --from=mcr.microsoft.com/dotnet/runtime:8.0 / /
# cuBLAS/cuDNN live at /usr/local/cuda/lib64 in this base; EP .so + libs resolve via this
ENV LD_LIBRARY_PATH=/usr/local/cuda/lib64
WORKDIR /app
COPY --from=build /app/publish .
ENTRYPOINT ["dotnet", "detector.dll"]