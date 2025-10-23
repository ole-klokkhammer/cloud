using System.Runtime.CompilerServices;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using RabbitMQ.Client;

public class RabbitMqService : IDisposable
{

    private readonly ConnectionFactory factory;
    private readonly ILogger<RabbitMqService> logger;

    private IConnection? connection = null;
    private readonly SemaphoreSlim connectionSemaphore = new(1, 1);

    public RabbitMqService(ILogger<RabbitMqService> logger)
    {
        this.logger = logger;
        factory = new ConnectionFactory
        {
            HostName = AppEnvironment.RabbitMqHost,
            UserName = AppEnvironment.RabbitMqUser,
            Password = AppEnvironment.RabbitMqPassword,
            AutomaticRecoveryEnabled = true,
            NetworkRecoveryInterval = TimeSpan.FromSeconds(10),
        };
    }


    public void Dispose()
    {
        connection?.Dispose();
    }

    public async Task<IChannel> CreateChannelAsync()
    {
        var conn = await GetConnection();
        return await conn.CreateChannelAsync();
    }


    public async Task PublishAsync(string exchange, string routingKey, ReadOnlyMemory<byte> body)
    {
        try
        {
            var channel = await CreateChannelAsync();
            await channel.BasicPublishAsync(
                exchange: exchange,
                routingKey: routingKey,
                body: body
            );
            await channel.CloseAsync();
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "Error publishing message to RabbitMQ");
            throw;
        }
    }

    private async Task<IConnection> CreateConnectionAsync()
    {
        await connectionSemaphore.WaitAsync();
        try
        {
            if (connection == null || !connection.IsOpen)
            {
                connection = await factory.CreateConnectionAsync();
            }
            return connection;
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "Failed to create RabbitMQ connection.");
            throw;
        }
        finally
        {
            connectionSemaphore.Release();
        }
    }

    private async Task<IConnection> GetConnection()
    {
        if (connection == null || !connection.IsOpen)
        {
            connection = await CreateConnectionAsync();
        }

        return connection;
    }
}