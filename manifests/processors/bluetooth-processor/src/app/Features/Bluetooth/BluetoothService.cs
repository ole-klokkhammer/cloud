using System.Text.Json;
using Microsoft.Extensions.Logging;

class BluetoothService
{
    private readonly ILogger<BluetoothService> logger;
    private readonly BluetoothRepository bluetoothRepository;
    private readonly AirthingsService airthingsService;

    private readonly JsonUtil json;

    public BluetoothService(
        ILogger<BluetoothService> logger,
        AirthingsService airthingsService,
        BluetoothRepository bluetoothRepository,
        JsonUtil json
    )
    {
        this.logger = logger;
        this.airthingsService = airthingsService;
        this.bluetoothRepository = bluetoothRepository;
        this.json = json;
    }

    public async Task HandleScan(string payload)
    {
        var scans = json.Deserialize<List<BluetoothScan>>(payload);
        if (scans == null || scans.Count == 0)
        {
            logger.LogWarning("No scan data found in message.");
            return;
        }

        foreach (var scan in scans)
        {
            await bluetoothRepository.InsertScanAsync(scan);
        }
        logger.LogInformation($"Inserted {scans.Count} bluetooth scan(s).");
    }

    public async Task HandleConnect(string key, string payload)
    {

        if (key.Contains(BleAirthingsConstants.ManufacturerId))
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
        if (key.Contains(BleAirthingsConstants.ManufacturerId))
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