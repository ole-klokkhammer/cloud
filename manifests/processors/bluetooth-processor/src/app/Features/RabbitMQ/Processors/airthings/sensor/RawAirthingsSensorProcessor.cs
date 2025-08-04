using System.Text;
using Microsoft.Extensions.Logging;
using RabbitMQ.Client;
using RabbitMQ.Client.Events;


public class RawAirthingsSensorProcessor : RabbitMqProcessorBase<RawAirthingsSensorProcessor>
{
    protected override string Exchange => "bluetooth";
    protected override string InboxRoutingKey => "airthings.sensor.raw";
    protected override string OutboxRoutingKey => "airthings.sensor.parsed";

    public RawAirthingsSensorProcessor(
        JsonUtil json,
        ILogger<RawAirthingsSensorProcessor> logger,
        RabbitMqService rabbitMqConnectionService
    ) : base(json, logger, rabbitMqConnectionService) { }

    protected override async Task OnMessage(IChannel channel, object model, BasicDeliverEventArgs ea)
    {
        var body = ea.Body.ToArray();
        var message = Encoding.UTF8.GetString(body);
        if (ea.BasicProperties.Headers?.TryGetValue("address", out var address) == true && address is byte[] addressBytes)
        {
            var addressString = Encoding.UTF8.GetString(addressBytes);
            await HandleConnectPayload(addressString, message);
            await channel.BasicAckAsync(deliveryTag: ea.DeliveryTag, multiple: false);
        }
        else
        {
            logger.LogWarning("No valid MAC address found in message headers.");
            await channel.BasicNackAsync(deliveryTag: ea.DeliveryTag, multiple: false, requeue: false);
            return;
        }
    }

    public async Task HandleConnectPayload(string mac, string payload)
    {
        logger.LogDebug($"Received connect payload for mac: {mac}");

        var data = json.Deserialize<GattRoot>(payload);
        if (data == null)
        {
            throw new ArgumentException("No data found in payload.");
        }

        logger.LogDebug("Parsing Airthings sensor data...");
        var airthingsSensor = data.ParseSensor(mac: mac, locationId: null);

        await base.PublishOutbox(airthingsSensor);
    }
}