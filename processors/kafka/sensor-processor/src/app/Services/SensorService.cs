using Confluent.Kafka;
using Microsoft.Extensions.Logging;
using Npgsql;

class SensorService
{
    private readonly ILogger<SensorService> logger;

    public SensorService(ILogger<SensorService> logger)
    {
        this.logger = logger;
    }

    public async Task<int> DoWork()
    { 
        logger.LogInformation("Starting sensor processor...");

        using var kafkaConsumer = new ConsumerBuilder<string, string>(
            new ConsumerConfig
            {
                BootstrapServers = AppEnvironment.KafkaBroker,
                AutoOffsetReset = AutoOffsetReset.Earliest,
                GroupId = "sensor-processor",
            }
        )
            .SetKeyDeserializer(Deserializers.Utf8)
            .SetValueDeserializer(Deserializers.Utf8)
            .Build();

        using var postgresConn = new NpgsqlConnection(
            @$"
                Host={AppEnvironment.DbHost};
                Port={AppEnvironment.DbPort};
                Username={AppEnvironment.DbUser};
                Password={AppEnvironment.DbPassword};
                Database={AppEnvironment.DbName}
            "
        );

        try
        {
            logger.LogInformation("Connecting to Kafka...");
            kafkaConsumer.Subscribe(AppEnvironment.KafkaTopic);
            logger.LogInformation($"Subscribed to Kafka topic: {AppEnvironment.KafkaTopic}");

            logger.LogInformation("Connecting to PostgreSQL database...");
            await postgresConn.OpenAsync();
            logger.LogInformation("Connected to PostgreSQL database.");

            var cts = new CancellationTokenSource();
            Console.CancelKeyPress += (_, e) => { e.Cancel = true; cts.Cancel(); };

            await ConsumeKafkaAsync(kafkaConsumer, postgresConn, cts.Token);
        }
        catch (Exception ex)
        {
            logger.LogError($"Fatal error: {ex.Message}");
            return 1;
        }
        finally
        {
            kafkaConsumer.Close();
            await postgresConn.CloseAsync();
            logger.LogInformation("Kafka consumer and DB connection closed.");
        }
        return 0;
    }

    async Task ConsumeKafkaAsync(IConsumer<string, string> consumer, NpgsqlConnection conn, CancellationToken token)
    {
        while (!token.IsCancellationRequested)
        {
            try
            {
                var cr = consumer.Consume(token);
                var key = cr.Message.Key;

                if (string.IsNullOrEmpty(key) || !key.StartsWith("bluetooth"))
                {
                    logger.LogDebug($"Skipping message with key: {key} from topic: {cr.Topic}");
                    continue;
                }
                var value = cr.Message.Value;
                if (string.IsNullOrWhiteSpace(value))
                {
                    logger.LogDebug("Received empty message from Kafka, skipping.");
                    continue;
                }

                await using var cmd = new NpgsqlCommand(
                    "INSERT INTO sensor (data) VALUES (@data::jsonb)",
                    conn
                );
                cmd.Parameters.AddWithValue("data", NpgsqlTypes.NpgsqlDbType.Jsonb, value);
                await cmd.ExecuteNonQueryAsync(token);
                logger.LogDebug("Inserted message into sensordb");
            }
            catch (ConsumeException ce)
            {
                logger.LogError($"Kafka consume error: {ce.Error.Reason}");
            }
            catch (OperationCanceledException)
            {
                logger.LogInformation("Cancellation requested, shutting down consume loop.");
                break;
            }
            catch (Exception e)
            {
                logger.LogError($"Database error: {e.Message}");
                try { await conn.BeginTransaction().RollbackAsync(); } catch { }
            }
        }
    }
}