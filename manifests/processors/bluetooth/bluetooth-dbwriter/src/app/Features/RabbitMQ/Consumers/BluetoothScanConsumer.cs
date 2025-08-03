using System.Text;
using Microsoft.Extensions.Logging;
using RabbitMQ.Client;
using RabbitMQ.Client.Events;


public class BluetoothScanConsumer(
    JsonUtil json,
    ILogger<BluetoothScanConsumer> logger,
    BluetoothRepository bluetoothRepository,
    RabbitMqConnectionService rabbitMqConnectionService
)
{
    private const string QueueName = "bluetooth.scan";

    public async Task Consume(CancellationToken token)
    {
        var connection = rabbitMqConnectionService.GetConnection();
        using var channel = await connection.CreateChannelAsync();

        await channel.QueueDeclareAsync(
            queue: QueueName,
            durable: true,
            exclusive: false,
            autoDelete: false,
            arguments: null
        );

        var consumer = new AsyncEventingBasicConsumer(channel);
        consumer.ReceivedAsync += async (model, ea) =>
        {
            try
            {
                var body = ea.Body.ToArray();
                var message = Encoding.UTF8.GetString(body);
                await HandleScan(message);
                await channel.BasicAckAsync(deliveryTag: ea.DeliveryTag, multiple: false);
            }
            catch (Exception ex)
            {
                logger.LogError(ex, "Error in BluetoothScanConsumer");
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
}