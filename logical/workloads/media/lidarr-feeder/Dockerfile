# ---- Build Stage ----
FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build

# Copy csproj and restore as distinct layers
COPY ./src/LidarrFeeder.csproj ./app/
RUN dotnet restore ./app/LidarrFeeder.csproj

# Copy the rest of the source code
COPY ./src ./app

# Build the application
WORKDIR /app
RUN dotnet publish LidarrFeeder.csproj -c Release -o /app/publish

# ---- Runtime Stage ----
FROM mcr.microsoft.com/dotnet/aspnet:9.0

WORKDIR /app

COPY --from=build /app/publish .

# Run the application
ENTRYPOINT ["dotnet", "LidarrFeeder.dll"]