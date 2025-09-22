

using System.Text;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using RabbitMQ.Client;
using RabbitMQ.Client.Events;

public abstract class RabbitMqConsumerBase<TConsumer> : BackgroundService
{
    private const string DEAD_LETTER_SUFFIX = "dlx";
    protected readonly JsonUtil json;
    protected readonly ILogger<TConsumer> logger;
    protected readonly RabbitMqService rabbitMq;
    protected abstract string Exchange { get; }
    protected abstract string InboxRoutingKey { get; }
    protected abstract string? OutboxRoutingKey { get; }

    protected virtual string QueueName => $"{Exchange}.{InboxRoutingKey}";
    protected virtual string RoutingKey => $"{InboxRoutingKey}";

    protected virtual string DeadLetterExchange => $"{Exchange}.{DEAD_LETTER_SUFFIX}";
    protected virtual string DeadLetterRoutingKey => $"{InboxRoutingKey}.{DEAD_LETTER_SUFFIX}";
    protected virtual string DeadLetterQueue => $"{Exchange}.{InboxRoutingKey}.{DEAD_LETTER_SUFFIX}";


    protected RabbitMqConsumerBase(
        JsonUtil json,
        ILogger<TConsumer> logger,
        RabbitMqService rabbitMq
    )
    {
        this.json = json;
        this.logger = logger;
        this.rabbitMq = rabbitMq;
    }

    protected override async Task ExecuteAsync(CancellationToken token)
    {

        while (!token.IsCancellationRequested)
        {
            try
            {
                logger.LogInformation($"Starting RabbitMQ consumer for {QueueName} queue...");
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
                logger.LogError(ex, $"Fatal error while running {typeof(TConsumer).Name} consumer.");
                logger.LogInformation($"Retrying {typeof(TConsumer).Name} consumer in 5 seconds...");
                await Task.Delay(5000, token);
            }
        }
        logger.LogInformation($"RabbitMQ consumer for {QueueName} queue stopped.");
    }

    private async Task OnReceivedAsync(IChannel channel, object model, BasicDeliverEventArgs ea)
    {
        try
        {
            logger.LogDebug($"Received message from {QueueName}: {Encoding.UTF8.GetString(ea.Body.ToArray())}");
            await OnMessage(model, ea);
            await channel.BasicAckAsync(deliveryTag: ea.DeliveryTag, multiple: false);
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "Error processing message from RabbitMQ.");
            await channel.BasicNackAsync(deliveryTag: ea.DeliveryTag, multiple: false, requeue: false);
        }
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
        await channel.ExchangeDeclareAsync(Exchange, "topic", true);
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
        await channel.QueueBindAsync(QueueName, Exchange, RoutingKey);
    }

    protected abstract Task OnMessage(object model, BasicDeliverEventArgs ea);

    protected async Task PublishOutbox<T>(T message)
    {
        if (string.IsNullOrEmpty(OutboxRoutingKey))
        {
            throw new InvalidOperationException("OutboxRoutingKey is not set.");
        }
        await rabbitMq.PublishAsync(
            exchange: Exchange,
            routingKey: OutboxRoutingKey,
            body: Encoding.UTF8.GetBytes(json.Serialize(message))
        );
    }
}