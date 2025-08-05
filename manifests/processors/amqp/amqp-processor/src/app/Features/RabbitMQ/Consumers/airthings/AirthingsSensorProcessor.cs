using System.Text;
using Microsoft.Extensions.Logging;
using RabbitMQ.Client;
using RabbitMQ.Client.Events;


public class AirthingsSensorProcessor : RabbitMqConsumerBase<AirthingsSensorProcessor>
{
    protected override string Exchange => "bluetooth";
    protected override string InboxRoutingKey => "airthings.sensor.raw";
    protected override string OutboxRoutingKey => "airthings.sensor.parsed";

    public AirthingsSensorProcessor(
        JsonUtil json,
        ILogger<AirthingsSensorProcessor> logger,
        RabbitMqService rabbitMqConnectionService
    ) : base(json, logger, rabbitMqConnectionService) { }

    protected override async Task OnMessage(object model, BasicDeliverEventArgs ea)
    {
        var body = ea.Body.ToArray();
        var message = Encoding.UTF8.GetString(body);
        if (ea.BasicProperties.Headers?.TryGetValue("address", out var address) == true && address is byte[] addressBytes)
        {
            var addressString = Encoding.UTF8.GetString(addressBytes);
            await HandleConnectPayload(addressString, message);
        }
        else
        {
            throw new Exception("No valid MAC address found in message headers.");
        }
    }

    public async Task HandleConnectPayload(string mac, string payload)
    {
        logger.LogDebug($"Received connect payload for mac: {mac}");

        var data = json.Deserialize<GattRoot>(payload);
        if (data == null)
        {
            throw new Exception("No data found in payload.");
        }

        logger.LogDebug("Parsing Airthings sensor data...");
        var airthingsSensor = data.ParseSensor(mac: mac, locationId: null);

        await base.PublishOutbox(airthingsSensor);
    }
}