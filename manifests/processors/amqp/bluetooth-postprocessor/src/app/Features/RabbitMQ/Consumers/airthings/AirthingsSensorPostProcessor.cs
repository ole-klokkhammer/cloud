using System.Text;
using Microsoft.Extensions.Logging;
using RabbitMQ.Client;
using RabbitMQ.Client.Events;


public class AirthingsSensorPostProcessor : RabbitMqConsumerBase<AirthingsSensorPostProcessor>
{
    protected override string Exchange => "bluetooth";
    protected override string InboxRoutingKey => "airthings.sensor.parsed";
    protected override string OutboxRoutingKey => null!;
    private const string MqttAirthingsTopicPrefix = "bluetooth/airthings";

    private readonly AirthingsRepository airthingsRepository;
    private readonly HomeassistantService homeassistantService;

    public AirthingsSensorPostProcessor(
        JsonUtil json,
        ILogger<AirthingsSensorPostProcessor> logger,
        RabbitMqService rabbitMqConnectionService,
        HomeassistantService homeassistantService,
        AirthingsRepository airthingsRepository
    ) : base(json, logger, rabbitMqConnectionService)
    {
        this.airthingsRepository = airthingsRepository;
        this.homeassistantService = homeassistantService;
    }

    protected override async Task OnMessage(object model, BasicDeliverEventArgs ea)
    {
        var body = ea.Body.ToArray();
        var message = Encoding.UTF8.GetString(body);
        var airthingsSensor = json.Deserialize<AirthingsSensor>(message);
        if (airthingsSensor == null)
        {
            throw new Exception("No data found in payload.");
        }

        logger.LogInformation($"Received parsed Airthings sensor data for MAC: {airthingsSensor.Mac}");
        logger.LogDebug($"Sensor data: {json.Serialize(airthingsSensor.SensorData)}");


        await airthingsRepository.InsertDeviceAsync(
            airthingsDevice: airthingsSensor.DeviceInfo,
            mac: airthingsSensor.Mac,
            locationId: airthingsSensor.LocationId
        );

        await airthingsRepository.InsertSensorDataAsync(
            sensorData: airthingsSensor.SensorData, serial:
            airthingsSensor.DeviceInfo.Serial
        );

        await TryHandleMqttPublish(airthingsSensor);
    }

    private async Task TryHandleMqttPublish(AirthingsSensor sensor)
    {
        try
        {
            var airthingsSensorData = sensor.SensorData;
            var airthingsDevice = sensor.DeviceInfo;
            await rabbitMqConnectionService.PublishMqttAsync($"{MqttAirthingsTopicPrefix}/{airthingsDevice.Serial}/data", json.Serialize(airthingsSensorData));
            await rabbitMqConnectionService.PublishMqttAsync($"{MqttAirthingsTopicPrefix}/{airthingsDevice.Serial}/device", json.Serialize(airthingsDevice));
            await homeassistantService.TryHomeAssistantAutoDiscoveryAirthingsSensor(sensor);
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "Failed to handle MQTT publish for Airthings sensor with MAC: {Mac}", sensor.Mac);
            return;
        }
    }
}