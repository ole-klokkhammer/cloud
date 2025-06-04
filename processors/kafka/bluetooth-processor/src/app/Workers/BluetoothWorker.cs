using System.Text.Json;
using Confluent.Kafka;
using Microsoft.Extensions.Logging;
using Npgsql;

class BluetoothWorker
{
    private readonly ILogger<BluetoothWorker> logger;
    private readonly ConsumerConfig kafkaConsumerConfig;
    private readonly BluetoothService bluetoothService;

    public BluetoothWorker(
        ILogger<BluetoothWorker> logger,
        BluetoothService bluetoothService
    )
    {
        this.logger = logger;
        this.bluetoothService = bluetoothService;
        this.kafkaConsumerConfig = new ConsumerConfig
        {
            BootstrapServers = AppEnvironment.KafkaBroker,
            AutoOffsetReset = AutoOffsetReset.Earliest,
            GroupId = "sensor-processor",
            EnableAutoCommit = false
        };
    }

    public async Task DoWork(CancellationToken token)
    {
        using (
            var kafkaConsumer = new ConsumerBuilder<string, string>(kafkaConsumerConfig)
                .SetKeyDeserializer(Deserializers.Utf8)
                .SetValueDeserializer(Deserializers.Utf8)
                .Build()
        )
        {
            try
            {
                kafkaConsumer.Subscribe(AppEnvironment.KafkaTopic);
                await KafkaConsumeLoop(kafkaConsumer, token);
            }
            catch (OperationCanceledException)
            {
                logger.LogInformation("Cancellation requested, shutting down consume loop.");
            }
            catch (Exception ex)
            {
                logger.LogError($"Fatal error: {ex.Message}");
            }
            finally
            {
                logger.LogInformation("Closing Kafka consumer...");
                kafkaConsumer.Unsubscribe();
                kafkaConsumer.Close();
            }
        }
    }

    async Task KafkaConsumeLoop(IConsumer<string, string> kafkaConsumer, CancellationToken token)
    {
        while (!token.IsCancellationRequested)
        {
            try
            {
                var cr = kafkaConsumer.Consume(token);
                var key = cr.Message.Key;
                var value = cr.Message.Value;

                if (string.IsNullOrEmpty(key))
                {
                    logger.LogDebug($"Skipping message with key: {key} from topic: {cr.Topic}");
                    continue;
                }

                if (string.IsNullOrWhiteSpace(value))
                {
                    logger.LogDebug("Received empty message from Kafka, skipping.");
                    continue;
                }

                if (key.StartsWith("scan"))
                {

                    logger.LogDebug($"Processing bluetooth scan: key: {key}");
                    await bluetoothService.HandleScan(value);
                    kafkaConsumer.Commit(cr);
                }

                if (key.StartsWith("connect"))
                {
                    logger.LogDebug($"Processing bluetooth connect: key: {key}");
                    await bluetoothService.HandleConnect(key, value);
                    kafkaConsumer.Commit(cr);
                }
            }
            catch (ConsumeException ce)
            {
                logger.LogError($"Kafka consume error: {ce.Error.Reason}");
            }
            catch (OperationCanceledException)
            {
                throw; // Propagate cancellation
            }
            catch (Exception ex)
            {
                logger.LogError($"Unexpected error in consume loop: {ex.Message}");
            }
        }
    }
}