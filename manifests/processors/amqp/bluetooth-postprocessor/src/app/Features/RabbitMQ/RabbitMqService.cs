
using System.Text;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using RabbitMQ.Client;

public class RabbitMqService : IHostedService
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

    public async Task StartAsync(CancellationToken cancellationToken)
    {
        consumerConnection = await factory.CreateConnectionAsync();
        producerConnection = await factory.CreateConnectionAsync();
    }

    public Task StopAsync(CancellationToken cancellationToken)
    {
        consumerConnection?.Dispose();
        producerConnection?.Dispose();
        return Task.CompletedTask;
    }

    public IConnection GetConnection() => consumerConnection;
    private IConnection GetProducerConnection() => producerConnection;


    public async Task PublishAsync(string exchange, string routingKey, ReadOnlyMemory<byte> body)
    {
        try
        {
            using var channel = await GetProducerConnection().CreateChannelAsync();

            await channel.BasicPublishAsync(
                exchange: exchange,
                routingKey: routingKey,
                body: body
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
                mandatory: true
            );
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "Error publishing Mqtt message to RabbitMQ");
        }
    }


}