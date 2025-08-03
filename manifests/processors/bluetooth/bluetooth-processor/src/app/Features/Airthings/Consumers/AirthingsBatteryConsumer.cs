
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using RabbitMQ.Client;
using RabbitMQ.Client.Events;


public class AirthingsBatteryConsumer(
    ILogger<AirthingsBatteryConsumer> logger,
    RabbitMqService rabbitMqConnectionService
) : BackgroundService
{
    private const string QueueName = "bluetooth.airthings.battery";
    private const string DeadLetterQueue = QueueName + ".dlx";
    private const string DeadLetterExchange = "bluetooth.dlx";
    private const string DeadLetterRoutingKey = "airthings.battery";
    private const string MqttAirthingsTopicPrefix = "bluetooth/airthings";

    protected override async Task ExecuteAsync(CancellationToken token)
    {
        var connection = rabbitMqConnectionService.GetConnection();
        using var channel = await connection.CreateChannelAsync();

        await channel.ExchangeDeclareAsync(
            exchange: DeadLetterExchange,
            type: "topic",
            durable: true
        );

        await channel.QueueDeclareAsync(
            queue: DeadLetterQueue,
            durable: true
        );

        await channel.QueueBindAsync(
            queue: DeadLetterQueue,
            exchange: DeadLetterExchange,
            routingKey: DeadLetterRoutingKey
        );

        await channel.QueueDeclareAsync(
            queue: QueueName,
            durable: true,
            exclusive: false,
            autoDelete: false,
            arguments: new Dictionary<string, object?>
            {
                { "x-dead-letter-exchange", DeadLetterExchange },
                { "x-dead-letter-routing-key", DeadLetterRoutingKey }
            }
        );

        var consumer = new AsyncEventingBasicConsumer(channel);
        consumer.ReceivedAsync += async (model, ea) =>
        {
            var body = ea.Body.ToArray();
            if (ea.BasicProperties.Headers?.TryGetValue("address", out var address) == true && address is string addressString)
            {
                await HandleCommandPayload(addressString, body);
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

    public async Task HandleCommandPayload(string mac, byte[] payload)
    {
        logger.LogInformation($"Received command payload for key: {mac}");
        logger.LogDebug($"Payload: {payload}");

        float batteryVolt = payload.ParseBatteryVolt();
        logger.LogDebug($"Battery voltage: {batteryVolt}V");

        int batteryLevel = batteryVolt.ParseBatteryPercentage();
        logger.LogDebug($"Battery percentage: {batteryLevel}%");

        logger.LogDebug("Publishing Airthings data to MQTT...");
        await rabbitMqConnectionService.PublishMqttAsync($"{MqttAirthingsTopicPrefix}/{mac}/battery/voltage", batteryVolt.ToString());
        await rabbitMqConnectionService.PublishMqttAsync($"{MqttAirthingsTopicPrefix}/{mac}/battery/percentage", batteryLevel.ToString());

    }
}