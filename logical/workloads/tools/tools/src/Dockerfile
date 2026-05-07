# ---- Build Stage ----
FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build

# Copy csproj and restore as distinct layers
COPY ./app/RabbitmqForwarder.csproj ./app/
RUN dotnet restore ./app/RabbitmqForwarder.csproj

# Copy the rest of the source code
COPY ./app ./app

# Build the application
WORKDIR /app
RUN dotnet publish RabbitmqForwarder.csproj -c Release -o /app/publish

# ---- Runtime Stage ----
FROM mcr.microsoft.com/dotnet/aspnet:9.0

WORKDIR /app

COPY --from=build /app/publish .

# Run the application
ENTRYPOINT ["dotnet", "RabbitmqForwarder.dll"]