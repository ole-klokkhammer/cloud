using System.Text.Json;
using Microsoft.Extensions.Logging;

class BluetoothService
{
    private readonly ILogger<BluetoothService> logger;
    private readonly PostgresService postgresService;
    private readonly AirthingsService airthingsService;

    public BluetoothService(
        ILogger<BluetoothService> logger,
        PostgresService postgresService,
        AirthingsService airthingsService
    )
    {
        this.logger = logger;
        this.postgresService = postgresService;
        this.airthingsService = airthingsService;
    }

    public async Task HandleScan(string payload)
    {
        var scans = JsonSerializer.Deserialize<List<BluetoothScan>>(payload);
        if (scans == null || scans.Count == 0)
        {
            logger.LogWarning("No scan data found in message.");
            return;
        }

        foreach (var scan in scans)
        {
            await postgresService.InsertDataAsync(
                @$"
                    INSERT INTO bluetooth.scan (
                        name, address, rssi, manufacturer_data
                    ) VALUES (
                        @name, @address, @rssi, @manufacturer_data
                    );
                ",
                new Dictionary<string, object>
                {
                    { "name", scan.name ?? (object)DBNull.Value },
                    { "address", scan.address ?? (object)DBNull.Value },
                    { "rssi", scan.rssi },
                    { "manufacturer_data", new Npgsql.NpgsqlParameter
                        {
                            ParameterName = "manufacturer_data",
                            NpgsqlDbType = NpgsqlTypes.NpgsqlDbType.Jsonb,
                            Value = scan.manufacturer_data != null ?
                                JsonSerializer.Serialize(scan.manufacturer_data)
                                : "{}"
                        }
                    }
                }
            );
        }
        logger.LogInformation($"Inserted {scans.Count} bluetooth scan(s).");
    }

    public async Task HandleConnect(string key, string payload)
    {

        if (key.Contains("airthings"))
        {
            logger.LogDebug($"Processing airthings connect: key: {key}");
            await airthingsService.HandleConnectPayload(key, payload);
        }
        else
        {
            logger.LogWarning($"Unknown bluetooth connect key: {key}");
        }
    }

    public async Task HandleCommand(string key, byte[] payload)
    {
        if (key.Contains("airthings"))
        {
            logger.LogDebug($"Processing airthings command: key: {key}");
            await airthingsService.HandleCommandPayload(key, payload);
        }
        else
        {
            logger.LogWarning($"Unknown bluetooth command key: {key}");
        }
    }
}