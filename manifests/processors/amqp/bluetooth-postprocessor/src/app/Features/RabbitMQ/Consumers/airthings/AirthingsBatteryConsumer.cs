
using System.Text;
using Microsoft.Extensions.Logging;
using RabbitMQ.Client;
using RabbitMQ.Client.Events;

public class AirthingsBatteryConsumer : RabbitMqConsumerBase<AirthingsBatteryConsumer>
{

    private readonly AirthingsRepository airthingsRepository;
    private readonly MqttService mqttService;

    public AirthingsBatteryConsumer(
        JsonUtil json,
        ILogger<AirthingsBatteryConsumer> logger,
        RabbitMqService rabbitmq,
        AirthingsRepository airthingsRepository,
        MqttService mqttService
    ) : base(json, logger, rabbitmq)
    {
        this.mqttService = mqttService;
        this.airthingsRepository = airthingsRepository;
    }

    protected override string Exchange => "bluetooth";
    protected override string InboxRoutingKey => "airthings.battery.parsed";
    protected override string OutboxRoutingKey => null!;
    private const string MqttAirthingsTopicPrefix = "bluetooth/airthings";

    protected override async Task OnMessage(object model, BasicDeliverEventArgs ea)
    {
        var body = ea.Body.ToArray();
        var message = Encoding.UTF8.GetString(body);
        var airthingsBatteryData = json.Deserialize<AirthingsBatteryData>(message);
        if (airthingsBatteryData == null)
        {
            throw new Exception("No data found in payload.");
        }

        logger.LogInformation($"Received parsed Airthings sensor data for MAC: {airthingsBatteryData.Mac}");
        logger.LogDebug($"Sensor data: {json.Serialize(airthingsBatteryData)}");

        var serial = await airthingsRepository.GetSerialByMacAsync(airthingsBatteryData.Mac);
        if (serial == null)
        {
            throw new Exception($"No serial found for MAC: {airthingsBatteryData.Mac}");
        }

        await airthingsRepository.InsertBatteryDataAsync(airthingsBatteryData, serial.Value);

        await TryHandleMqttPublish(airthingsBatteryData, serial.Value);
    }

    private async Task TryHandleMqttPublish(AirthingsBatteryData sensor, int serial)
    {
        try
        {
            var mac = sensor.Mac;
            var batteryVolt = sensor.Voltage;
            var batteryLevel = sensor.BatteryLevel;
            logger.LogInformation($"Publishing MQTT for Airthings battery with serial: {serial}, MAC: {mac}, Voltage: {batteryVolt}, Level: {batteryLevel}");
            await mqttService.PublishAsync($"{MqttAirthingsTopicPrefix}/{serial}/battery/voltage", batteryVolt.ToString());
            await mqttService.PublishAsync($"{MqttAirthingsTopicPrefix}/{serial}/battery/percentage", batteryLevel.ToString());
        }
        catch (Exception ex)
        {
            logger.LogError(ex, $"Failed to handle MQTT publish for Airthings sensor with serial: {serial},  MAC: {sensor.Mac}");
            return;
        }
    }
}