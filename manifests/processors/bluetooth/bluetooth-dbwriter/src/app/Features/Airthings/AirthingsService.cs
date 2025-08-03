using Microsoft.Extensions.Logging;

class AirthingsService
{
    private readonly ILogger<AirthingsService> logger;
    private readonly AirthingsRepository airthingsRepository;
    private readonly MqttService mqttService;
    private readonly HomeassistantService homeassistantService;

    private readonly JsonUtil json;

    private const string AirthingsTopicPrefix = "bluetooth/airthings";

    public AirthingsService(
        ILogger<AirthingsService> logger,
        AirthingsRepository airthingsRepository,
        HomeassistantService homeassistantService,
        MqttService mqttService,
        JsonUtil json
    )
    {
        this.logger = logger;
        this.airthingsRepository = airthingsRepository;
        this.mqttService = mqttService;
        this.json = json;
        this.homeassistantService = homeassistantService;
    }

    public async Task HandleCommandPayload(string kafkaKey, byte[] payload)
    {
        logger.LogInformation($"Received command payload for key: {kafkaKey}");
        logger.LogDebug($"Payload: {payload}");

        float batteryVolt = payload.ParseBatteryVolt();
        logger.LogDebug($"Battery voltage: {batteryVolt}V");

        int batteryLevel = batteryVolt.ParseBatteryPercentage();
        logger.LogDebug($"Battery percentage: {batteryLevel}%");

        var mac = kafkaKey.Split('/')[2];
        var serial = await airthingsRepository.GetSerialByMacAsync(mac);
        if (serial == null)
        {
            throw new ArgumentException($"Could not find serial based on kafkaKey: {kafkaKey}");
        }

        var batteryData = new AirthingsBatteryData
        {
            Serial = serial.Value,
            BatteryLevel = batteryLevel,
            Voltage = batteryVolt
        };
        await airthingsRepository.InsertBatteryDataAsync(batteryData);

        logger.LogDebug("Publishing Airthings data to MQTT...");
        await mqttService.TryPublishAsync($"{AirthingsTopicPrefix}/{serial.Value}/battery", batteryData, retain: true);
    }

    public async Task HandleConnectPayload(string kafkaKey, string payload)
    {
        logger.LogDebug($"Received connect payload for key: {kafkaKey}");

        var data = json.Deserialize<GattRoot>(payload);
        if (data == null)
        {
            logger.LogWarning("No data found in payload.");
            return;
        }

        var mac = kafkaKey.Split('/').LastOrDefault();
        if (string.IsNullOrEmpty(mac))
        {
            throw new ArgumentException("MAC address not found in Kafka key.");
        }

        var airthingsDevice = data.ParseDeviceInfo(mac, logger);
        if (airthingsDevice == null)
        {
            throw new ArgumentException("Airthings device info not found in data.");
        }
        logger.LogDebug("Inserting Airthings device into database...");
        await airthingsRepository.InsertDeviceAsync(airthingsDevice);

        logger.LogDebug("Parsing Airthings sensor data...");
        var airthingsSensorData = data.ParseSensorData(airthingsDevice!.Serial, airthingsDevice.LocationId, logger);
        if (airthingsSensorData == null)
        {
            throw new ArgumentException("Airthings sensor data not found in data.");
        }
        logger.LogDebug("Inserting Airthings sensor data into database...");
        await airthingsRepository.InsertSensorDataAsync(airthingsSensorData);

        logger.LogDebug("Publishing Airthings data to MQTT...");
        await mqttService.TryPublishAsync($"{AirthingsTopicPrefix}/{airthingsDevice.Serial}/data", airthingsSensorData, retain: true);
        await mqttService.TryPublishAsync($"{AirthingsTopicPrefix}/{airthingsDevice.Serial}/device", airthingsDevice, retain: true);

        // Publish to Home Assistant for autodiscovery
        await homeassistantService.TryUpdateAirthingsHomeAssistantAutoDiscovery(airthingsDevice.Serial);
    }

}

