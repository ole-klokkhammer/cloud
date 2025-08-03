using System.Text;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using RabbitMQ.Client;
using RabbitMQ.Client.Events;


public class AirthingsSensorConsumer(
    JsonUtil json,
    ILogger<AirthingsSensorConsumer> logger,
    RabbitMqService rabbitMqConnectionService,
    HomeassistantService homeassistantService
) : BackgroundService
{
    private const string Exchange = "bluetooth";
    private const string QueueName = "bluetooth.airthings.sensor";
    private const string RoutingKey = "airthings.sensor";
    private const string DeadLetterQueue = QueueName + ".dlx";
    private const string DeadLetterExchange = "bluetooth.dlx";
    private const string MqttAirthingsTopicPrefix = "bluetooth/airthings";

    protected override async Task ExecuteAsync(CancellationToken token)
    {
        var connection = rabbitMqConnectionService.GetConnection();
        using var channel = await connection.CreateChannelAsync();

        // DEAD LETTER EXCHANGE AND QUEUE   
        await channel.ExchangeDeclareAsync(
            exchange: DeadLetterExchange,
            type: "topic",
            durable: true
        );

        await channel.QueueDeclareAsync(
            queue: DeadLetterQueue,
            durable: true,
            exclusive: false,
            autoDelete: false
        );

        await channel.QueueBindAsync(
            queue: DeadLetterQueue,
            exchange: DeadLetterExchange,
            routingKey: RoutingKey
        );

        // MAIN EXCHANGE AND QUEUE
        await channel.ExchangeDeclareAsync(
            exchange: Exchange,
            type: "topic",
            durable: true
        );

        await channel.QueueDeclareAsync(
            queue: QueueName,
            durable: true,
            exclusive: false,
            autoDelete: false,
            arguments: new Dictionary<string, object?>
            {
                { "x-dead-letter-exchange", DeadLetterExchange },
                { "x-dead-letter-routing-key", RoutingKey }
            }
        );

        await channel.QueueBindAsync(
            queue: QueueName,
            exchange: Exchange,
            routingKey: RoutingKey
        );

        var consumer = new AsyncEventingBasicConsumer(channel);
        consumer.ReceivedAsync += async (model, ea) =>
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
        };

        await channel.BasicConsumeAsync(
            queue: QueueName,
            autoAck: false,
            consumer: consumer
        );

        logger.LogInformation($"RabbitMQ consumer started for {QueueName} queue.");

        while (!token.IsCancellationRequested)
        {
            await Task.Delay(1000, token);
        }
    }

    public async Task HandleConnectPayload(string mac, string payload)
    {
        logger.LogDebug($"Received connect payload for mac: {mac}");

        var data = json.Deserialize<GattRoot>(payload);
        if (data == null)
        {
            logger.LogWarning("No data found in payload.");
            return;
        }

        var airthingsDevice = data.ParseDeviceInfo(mac, logger);
        if (airthingsDevice == null)
        {
            throw new ArgumentException("Airthings device info not found in data.");
        }


        logger.LogDebug("Parsing Airthings sensor data...");
        var airthingsSensorData = data.ParseSensorData(airthingsDevice!.Serial, airthingsDevice.LocationId, logger);
        if (airthingsSensorData == null)
        {
            throw new ArgumentException("Airthings sensor data not found in data.");
        }


        logger.LogDebug("Publishing Airthings data to MQTT...");
        await rabbitMqConnectionService.PublishMqttAsync($"{MqttAirthingsTopicPrefix}/{airthingsDevice.Serial}/data", json.Serialize(airthingsSensorData));
        await rabbitMqConnectionService.PublishMqttAsync($"{MqttAirthingsTopicPrefix}/{airthingsDevice.Serial}/device", json.Serialize(airthingsDevice));

        // Publish to Home Assistant for autodiscovery
        await homeassistantService.TryUpdateAirthingsHomeAssistantAutoDiscovery(airthingsDevice.Serial);
    }
}