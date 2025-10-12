# ---- Build Stage ----
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build

# Copy csproj and restore as distinct layers
COPY ./app/CameraRecorder.csproj ./app/
RUN dotnet restore ./app/CameraRecorder.csproj

# Copy the rest of the source code
COPY ./app ./app

# Build the application
WORKDIR /app
RUN dotnet publish CameraRecorder.csproj -c Release -o /app/publish

# ---- Runtime Stage ----
FROM mcr.microsoft.com/dotnet/aspnet:8.0

WORKDIR /app

# Install ffmpeg + fonts (fontconfig + DejaVu), refresh cache, clean
RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      ffmpeg \
 && rm -rf /var/lib/apt/lists/* 

COPY --from=build /app/publish .

# Run the application
ENTRYPOINT ["dotnet", "CameraRecorder.dll"]