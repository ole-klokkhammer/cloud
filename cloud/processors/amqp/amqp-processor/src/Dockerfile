# ---- Build Stage ----
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build

# Copy csproj and restore as distinct layers
COPY ./app/AmqpProcessor.csproj ./app/
RUN dotnet restore ./app/AmqpProcessor.csproj

# Copy the rest of the source code
COPY ./app ./app

# Build the application
WORKDIR /app
RUN dotnet publish AmqpProcessor.csproj -c Release -o /app/publish

# ---- Runtime Stage ----
FROM mcr.microsoft.com/dotnet/aspnet:8.0

WORKDIR /app

COPY --from=build /app/publish .

# Run the application
ENTRYPOINT ["dotnet", "AmqpProcessor.dll"]