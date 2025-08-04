
using System.Text;
using Microsoft.Extensions.Logging;
using RabbitMQ.Client;
using RabbitMQ.Client.Events;


public class RawAirthingsBatteryProcessor : RabbitMqProcessorBase<RawAirthingsBatteryProcessor>
{
    public RawAirthingsBatteryProcessor(
        JsonUtil json,
        ILogger<RawAirthingsBatteryProcessor> logger,
        RabbitMqService rabbitMqConnectionService
    ) : base(json, logger, rabbitMqConnectionService) { }

    protected override string Exchange => "bluetooth";
    protected override string InboxRoutingKey => "airthings.battery.raw";
    protected override string OutboxRoutingKey => "airthings.battery.parsed";

    protected override async Task OnMessage(IChannel channel, object model, BasicDeliverEventArgs ea)
    {
        var body = ea.Body.ToArray();
        if (ea.BasicProperties.Headers?.TryGetValue("address", out var address) == true && address is byte[] addressBytes)
        {
            var addressString = Encoding.UTF8.GetString(addressBytes);
            await HandleCommandPayload(addressString, body);
            await channel.BasicAckAsync(deliveryTag: ea.DeliveryTag, multiple: false);
        }
        else
        {
            logger.LogWarning("No valid MAC address found in message headers.");
            await channel.BasicNackAsync(deliveryTag: ea.DeliveryTag, multiple: false, requeue: false);
            return;
        }
    }

    public async Task HandleCommandPayload(string mac, byte[] payload)
    {
        logger.LogInformation($"Received command payload for key: {mac}");
        logger.LogDebug($"Payload: {payload}");

        float batteryVolt = payload.ParseBatteryVolt();
        logger.LogDebug($"Battery voltage: {batteryVolt}V");

        int batteryLevel = batteryVolt.ParseBatteryPercentage();
        logger.LogDebug($"Battery percentage: {batteryLevel}%");

        await base.PublishOutbox(new AirthingsBatteryData
        {
            Mac = mac,
            BatteryLevel = batteryLevel,
            Voltage = batteryVolt
        });
    }
}