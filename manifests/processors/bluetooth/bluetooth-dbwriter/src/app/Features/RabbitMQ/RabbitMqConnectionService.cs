using RabbitMQ.Client;

public class RabbitMqConnectionService : IDisposable
{
    private readonly ConnectionFactory factory;

    private IConnection connection = null!;

    public RabbitMqConnectionService()
    {
        factory = new ConnectionFactory
        {
            HostName = AppEnvironment.RabbitMqHost,
            UserName = AppEnvironment.RabbitMqUser,
            Password = AppEnvironment.RabbitMqPassword
        };
    }

    public async Task InitializeAsync()
    {
        connection = await factory.CreateConnectionAsync();
    }

    public IConnection GetConnection() => connection;

    public void Dispose()
    {
        connection?.Dispose();
    }
}