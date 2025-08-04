
using System.Text;
using Microsoft.Extensions.Logging;
using RabbitMQ.Client;
using RabbitMQ.Client.Events;

public class ParsedAirthingsBatteryProcessor : RabbitMqProcessorBase<ParsedAirthingsBatteryProcessor>
{

    private readonly AirthingsRepository airthingsRepository;

    public ParsedAirthingsBatteryProcessor(
        JsonUtil json,
        ILogger<ParsedAirthingsBatteryProcessor> logger,
        RabbitMqService rabbitMqConnectionService,
        AirthingsRepository airthingsRepository
    ) : base(json, logger, rabbitMqConnectionService)
    {
        this.airthingsRepository = airthingsRepository;
    }

    protected override string Exchange => "bluetooth";
    protected override string InboxRoutingKey => "airthings.battery.parsed";
    protected override string OutboxRoutingKey => null!;
    private const string MqttAirthingsTopicPrefix = "bluetooth/airthings";

    protected override async Task OnMessage(IChannel channel, object model, BasicDeliverEventArgs ea)
    {
        var body = ea.Body.ToArray();
        var message = Encoding.UTF8.GetString(body);
        var airthingsBatteryData = json.Deserialize<AirthingsBatteryData>(message);
        if (airthingsBatteryData == null)
        {
            throw new ArgumentException("No data found in payload.");
        }

        logger.LogInformation($"Received parsed Airthings sensor data for MAC: {airthingsBatteryData.Mac}");
        logger.LogDebug($"Sensor data: {json.Serialize(airthingsBatteryData)}");

        await TryHandleMqttPublish(airthingsBatteryData);

        var serial = await airthingsRepository.GetSerialByMacAsync(airthingsBatteryData.Mac);
        if (serial == null)
        {
            throw new ArgumentException($"No serial found for MAC: {airthingsBatteryData.Mac}");
        }

        await airthingsRepository.InsertBatteryDataAsync(airthingsBatteryData, serial.Value);
    }

    private async Task TryHandleMqttPublish(AirthingsBatteryData sensor)
    {
        try
        {
            var mac = sensor.Mac;
            var batteryVolt = sensor.Voltage;
            var batteryLevel = sensor.BatteryLevel;
            logger.LogInformation($"Publishing MQTT for Airthings battery with MAC: {mac}, Voltage: {batteryVolt}, Level: {batteryLevel}");
            await rabbitMqConnectionService.PublishMqttAsync($"{MqttAirthingsTopicPrefix}/{mac}/battery/voltage", batteryVolt.ToString());
            await rabbitMqConnectionService.PublishMqttAsync($"{MqttAirthingsTopicPrefix}/{mac}/battery/percentage", batteryLevel.ToString());
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "Failed to handle MQTT publish for Airthings sensor with MAC: {Mac}", sensor.Mac);
            return;
        }
    }
}