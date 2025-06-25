using System.Text.Json;
using Microsoft.Extensions.Logging;
using MQTTnet;
using MQTTnet.Client;
using MQTTnet.Diagnostics;

class MqttService
{
    private readonly IMqttClient mqttClient;
    private readonly ILogger<MqttService> logger;

    private readonly JsonUtil json;

    private readonly string broker;
    private readonly int port;
    private readonly string clientId;

    public MqttService(
        ILogger<MqttService> logger,
        JsonUtil json
    )
    { 
        this.mqttClient = new MqttFactory().CreateMqttClient();
        this.logger = logger;
        this.json = json;
        this.broker = AppEnvironment.MqttBroker;
        this.port = int.Parse(AppEnvironment.MqttPort);
        this.clientId = AppEnvironment.MqttClientId;
    }

    public async Task Initialize()
    {
        try
        {
            await mqttClient.ConnectAsync(
                new MqttClientOptionsBuilder()
                    .WithTcpServer(broker, port)
                    .WithClientId(clientId)
                    .Build()
            );
            logger.LogInformation("Connected to MQTT broker at {Broker}:{Port}", broker, port);
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "Failed to connect to MQTT broker");
            throw;
        }
    }

    public async Task Shutdown()
    {
        try
        {
            if (mqttClient.IsConnected)
            {
                await mqttClient.DisconnectAsync();
                logger.LogInformation("Disconnected from MQTT broker");
            }
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "Failed to disconnect from MQTT broker");
        }
    }

    public async Task SubscribeAsync(string topic)
    {
        try
        {
            await mqttClient.SubscribeAsync(new MqttTopicFilterBuilder().WithTopic(topic).Build());
            logger.LogInformation("Subscribed to topic {Topic}", topic);
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "Failed to subscribe to topic {Topic}", topic);
            throw;
        }
    }

    public async Task<bool> TryPublishAsync<T>(string topic, T message, bool retain = false)
    where T : class
    {
        try
        {
            var mqttMessage = new MqttApplicationMessageBuilder()
                .WithTopic(topic)
                .WithPayload(json.Serialize(message))
                .WithRetainFlag(retain)
                .Build();

            await mqttClient.PublishAsync(mqttMessage);
            logger.LogInformation("Published message to topic {Topic}: {Message}", topic, message);
            return true;
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "Failed to publish message to topic {Topic}", topic);
            return false;
        }
    }
}