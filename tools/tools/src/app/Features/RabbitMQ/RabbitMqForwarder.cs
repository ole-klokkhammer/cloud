
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using RabbitMQ.Client;
using RabbitMQ.Client.Events;

public class RabbitMqForwarder(
        ILogger<RabbitMqForwarder> logger,
        RabbitMqService rabbitMq,
        HttpClient httpClient,
        string rabbitmqExchange,
        string rabbitmqInbox,
        string httpEndpoint
    ) : BackgroundService
{
    private const string DEAD_LETTER_SUFFIX = "dlx";

    private string QueueName => $"{rabbitmqExchange}.{rabbitmqInbox}";
    private string RoutingKey => $"{rabbitmqInbox}";
    private string DeadLetterExchange => $"{rabbitmqExchange}.{DEAD_LETTER_SUFFIX}";
    private string DeadLetterRoutingKey => $"{rabbitmqInbox}.{DEAD_LETTER_SUFFIX}";
    private string DeadLetterQueue => $"{rabbitmqExchange}.{rabbitmqInbox}.{DEAD_LETTER_SUFFIX}";

    protected override async Task ExecuteAsync(CancellationToken token)
    {
        while (!token.IsCancellationRequested)
        {
            try
            {
                logger.LogInformation($"Starting RabbitMQ consumer (sidecar) for {QueueName} queue, forwarding to {httpEndpoint} ...");
                using var channel = await rabbitMq.CreateChannelAsync();
                await PrepareExchangeAndQueueAsync(channel);

                var consumer = new AsyncEventingBasicConsumer(channel);
                consumer.ReceivedAsync += async (model, ea) =>
                {
                    await OnReceivedAsync(channel, model, ea);
                };

                await channel.BasicConsumeAsync(queue: QueueName, autoAck: false, consumer: consumer);
                logger.LogInformation($"RabbitMQ consumer started for {QueueName} queue.");

                while (!token.IsCancellationRequested)
                {
                    await Task.Delay(1000, token);
                }
            }
            catch (Exception ex)
            {
                logger.LogError(ex, $"Fatal error while running {typeof(RabbitMqForwarder).Name} sidecar consumer.");
                logger.LogInformation($"Retrying {typeof(RabbitMqForwarder).Name} consumer in 5 seconds...");
                await Task.Delay(5000, token);
            }
        }
        logger.LogInformation($"RabbitMQ consumer for {QueueName} queue stopped.");
    }

    private async Task OnReceivedAsync(IChannel channel, object model, BasicDeliverEventArgs ea)
    {
        string payload = Encoding.UTF8.GetString(ea.Body.ToArray());
        logger.LogDebug($"Sidecar received message from {QueueName}: {payload}");

        try
        {
            // Allow subclasses to transform/validate the payload before sending
            var contentBytes = await TransformPayloadAsync(payload, ea);

            using var content = new ByteArrayContent(contentBytes);
            content.Headers.ContentType = new MediaTypeHeaderValue("application/json");

            using var request = new HttpRequestMessage(HttpMethod.Post, httpEndpoint)
            {
                Content = content
            };

            // Send to configured API endpoint
            var response = await httpClient.SendAsync(request);

            if (response.IsSuccessStatusCode)
            {
                logger.LogInformation($"Successfully forwarded message from {QueueName} to {httpEndpoint} (status {response.StatusCode}).");
                await channel.BasicAckAsync(deliveryTag: ea.DeliveryTag, multiple: false);
            }
            else
            {
                string respBody = await response.Content.ReadAsStringAsync();
                logger.LogError("Failed to forward message to API. Status: {StatusCode}, Body: {Body}", response.StatusCode, respBody);
                // Nack without requeue so message goes to dead-letter exchange configured on the queue
                await channel.BasicNackAsync(deliveryTag: ea.DeliveryTag, multiple: false, requeue: false);
            }
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "Error processing/forwarding message from RabbitMQ.");
            await channel.BasicNackAsync(deliveryTag: ea.DeliveryTag, multiple: false, requeue: false);
        }
    }

    // Default implementation returns the original UTF8 JSON bytes.
    // Override to transform, enrich, or validate message before POSTing to the API.
    protected virtual Task<byte[]> TransformPayloadAsync(string payload, BasicDeliverEventArgs ea)
    {
        return Task.FromResult(Encoding.UTF8.GetBytes(payload));
    }

    protected virtual async Task PrepareExchangeAndQueueAsync(IChannel channel)
    {
        // deadletter queue 
        await channel.ExchangeDeclareAsync(DeadLetterExchange, "topic", true);
        await channel.QueueDeclareAsync(
            queue: DeadLetterQueue,
            durable: true,
             exclusive: false,
              autoDelete: false
        );
        await channel.QueueBindAsync(DeadLetterQueue, DeadLetterExchange, DeadLetterRoutingKey);

        // Declare the main exchange and queue
        await channel.ExchangeDeclareAsync(rabbitmqExchange, "topic", true);
        await channel.QueueDeclareAsync(
            queue: QueueName,
            durable: true,
            exclusive: false,
            autoDelete: false,
            new Dictionary<string, object?>
            {
                { "x-dead-letter-exchange", DeadLetterExchange },
                { "x-dead-letter-routing-key", DeadLetterRoutingKey }
            }
        );
        await channel.QueueBindAsync(QueueName, rabbitmqExchange, RoutingKey);
    }
}