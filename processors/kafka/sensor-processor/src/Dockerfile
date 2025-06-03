# ---- Build Stage ----
FROM mcr.microsoft.com/dotnet/sdk:7.0 AS build

# Copy csproj and restore as distinct layers
COPY ./app/SensorProcessor.csproj ./app/
RUN dotnet restore ./app/SensorProcessor.csproj

# Copy the rest of the source code
COPY ./app ./app

# Build the application
WORKDIR /app
RUN dotnet publish SensorProcessor.csproj -c Release -o /app/publish

# ---- Runtime Stage ----
FROM mcr.microsoft.com/dotnet/aspnet:7.0

WORKDIR /app

COPY --from=build /app/publish .

# Run the application
ENTRYPOINT ["dotnet", "SensorProcessor.dll"]