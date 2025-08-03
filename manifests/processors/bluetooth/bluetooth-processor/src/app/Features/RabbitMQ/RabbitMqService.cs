
using System.Text;
using Microsoft.Extensions.Logging;
using RabbitMQ.Client;

public class RabbitMqService : IDisposable
{
    private readonly ConnectionFactory factory;
    private readonly ILogger<RabbitMqService> logger;

    private IConnection consumerConnection = null!;
    private IConnection producerConnection = null!;

    public RabbitMqService(ILogger<RabbitMqService> logger)
    {
        this.logger = logger;
        factory = new ConnectionFactory
        {
            HostName = AppEnvironment.RabbitMqHost,
            UserName = AppEnvironment.RabbitMqUser,
            Password = AppEnvironment.RabbitMqPassword
        };
    }

    public async Task Initialize()
    {
        consumerConnection = await factory.CreateConnectionAsync();
        producerConnection = await factory.CreateConnectionAsync();
    }

    public IConnection GetConnection() => consumerConnection;
    private IConnection GetProducerConnection() => producerConnection;

    public void Dispose()
    {
        consumerConnection?.Dispose();
        producerConnection?.Dispose();
    }

    public async Task PublishAsync(string queueName, string message)
    {
        try
        {
            using var channel = await GetProducerConnection().CreateChannelAsync();

            await channel.QueueDeclareAsync(
                queue: queueName,
                durable: false,
                exclusive: false,
                autoDelete: false,
                arguments: null
            );

            await channel.BasicPublishAsync(
                exchange: string.Empty,
                routingKey: queueName,
                body: Encoding.UTF8.GetBytes(message)
            );
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "Error publishing message to RabbitMQ");
        }
    }

    public async Task PublishMqttAsync(string topic, string payload, bool retain = true, int qos = 0)
    {
        try
        {
            using var channel = await GetProducerConnection().CreateChannelAsync();
            await channel.BasicPublishAsync(
                exchange: "amq.topic",
                routingKey: topic,
                body: Encoding.UTF8.GetBytes(payload),
                basicProperties: new BasicProperties
                {
                    Headers = new Dictionary<string, object?>
                    {
                        { "x-mqtt-retain", retain },
                        { "x-mqtt-qos", qos }
                    }
                },
                mandatory: false
            );
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "Error publishing Mqtt message to RabbitMQ");
        }
    }
}