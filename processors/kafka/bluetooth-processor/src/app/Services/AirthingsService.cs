using System.Text.Json;
using Confluent.Kafka;
using Microsoft.Extensions.Logging;
using Npgsql;

class AirthingsService
{
    private readonly ILogger<AirthingsService> logger;

    public AirthingsService(ILogger<AirthingsService> logger)
    {
        this.logger = logger;
    }

    public async Task OnConnect(string payload)
    {

    }

}