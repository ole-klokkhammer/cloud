using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using MQTTnet;

public class MqttService : BackgroundService
{
    private readonly ILogger<MqttService> logger;
    private IMqttClient mqttClient;
    private MqttClientOptions mqttOptions;

    private int clientReconnectAttempts = 3;

    public MqttService(ILogger<MqttService> logger)
    {
        this.logger = logger;
        var factory = new MqttClientFactory();
        mqttClient = factory.CreateMqttClient();
        mqttOptions = new MqttClientOptionsBuilder()
          .WithTcpServer(AppEnvironment.MqttHost)
          .Build();
    }

    protected override async Task ExecuteAsync(CancellationToken token)
    {
        await ConnectAsync(); // throw exception if no connect on startup
        mqttClient.DisconnectedAsync += async e =>
        {
            await OnDisonnected(e, token);
        };

        while (!token.IsCancellationRequested)
        {
            await Task.Delay(1000, token);
        }

        logger.LogInformation("Stopping MQTT service...");
        if (mqttClient.IsConnected)
        {
            await mqttClient.DisconnectAsync();
        }
    }

    private async Task OnDisonnected(MqttClientDisconnectedEventArgs e, CancellationToken token)
    {
        logger.LogWarning($"MQTT disconnected. Will attempt to reconnect up to {clientReconnectAttempts} times...");
        int attempts = 0;
        while (attempts < clientReconnectAttempts && !mqttClient.IsConnected)
        {
            attempts++;
            try
            {
                await Task.Delay(TimeSpan.FromSeconds(5), token);
                await ConnectAsync();
                if (mqttClient.IsConnected)
                {
                    logger.LogInformation("Reconnected to MQTT broker.");
                    break;
                }
            }
            catch (Exception ex)
            {
                logger.LogError(ex, $"Reconnect attempt {attempts} failed.");
            }
        }
        if (!mqttClient.IsConnected)
        {
            logger.LogError("Failed to reconnect to MQTT broker after 3 attempts. Service will stop.");
            throw new Exception("MQTT reconnect failed after 3 attempts.");
        }
    }

    public async Task PublishAsync(string topic, string payload, bool retain = true)
    {
        if (!mqttClient.IsConnected)
        {
            logger.LogWarning("MQTT client is not connected. Cannot publish message.");
            return;
        }

        var message = new MqttApplicationMessageBuilder()
            .WithTopic(topic)
            .WithPayload(payload)
            .WithRetainFlag(retain)
            .Build();

        await mqttClient.PublishAsync(message);
        logger.LogDebug($"Published message to topic '{topic}': {payload}");
    }


    private async Task ConnectAsync()
    {
        try
        {
            if (mqttClient.IsConnected)
            {
                logger.LogInformation("MQTT client is already connected.");
                return;
            }
            await mqttClient.ConnectAsync(mqttOptions);
            logger.LogInformation("Connected to MQTT broker.");
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "MQTT connection failed.");
            throw;
        }
    }
}