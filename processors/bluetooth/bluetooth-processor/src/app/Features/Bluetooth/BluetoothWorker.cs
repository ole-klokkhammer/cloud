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
            GroupId = "bluetooth-processor",
            EnableAutoCommit = false
        };
    }

    public async Task DoWork(CancellationToken token)
    {
        using (
            var kafkaConsumer = new ConsumerBuilder<string, byte[]>(kafkaConsumerConfig)
                .SetKeyDeserializer(Deserializers.Utf8)
                .SetValueDeserializer(Deserializers.ByteArray)
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

    async Task KafkaConsumeLoop(IConsumer<string, byte[]> kafkaConsumer, CancellationToken token)
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

                if (value == null || value.Length == 0)
                {
                    logger.LogDebug($"Skipping message with empty value for key: {key}");
                    continue;
                } 

                if (key.StartsWith("scan"))
                {

                    logger.LogDebug($"Processing bluetooth scan: key: {key}"); 
                    await bluetoothService.HandleScan(System.Text.Encoding.UTF8.GetString(value));
                    kafkaConsumer.Commit(cr);
                }

                if (key.StartsWith("connect"))
                {
                    logger.LogDebug($"Processing bluetooth connect: key: {key}");
                    await bluetoothService.HandleConnect(key, System.Text.Encoding.UTF8.GetString(value));
                    kafkaConsumer.Commit(cr);
                }

                if (key.StartsWith("command"))
                {
                    logger.LogDebug($"Processing bluetooth command: key: {key}");
                    await bluetoothService.HandleCommand(key, value);
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