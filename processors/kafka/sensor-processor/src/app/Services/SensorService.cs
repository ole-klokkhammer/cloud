using System.Text.Json;
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
            logger.LogInformation("Closing Kafka consumer...");
            kafkaConsumer.Close();
            logger.LogInformation("Closing PostgreSQL connection...");
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
                var value = cr.Message.Value;

                if (string.IsNullOrEmpty(key) || !key.StartsWith("bluetooth"))
                {
                    logger.LogDebug($"Skipping message with key: {key} from topic: {cr.Topic}");
                    continue;
                }

                if (string.IsNullOrWhiteSpace(value))
                {
                    logger.LogDebug("Received empty message from Kafka, skipping.");
                    continue;
                }

                if (key.StartsWith("bluetooth/airthings") && key.Split('/').Length == 3)
                {
                    var name = key.Split('/')[2];
                    logger.LogDebug($"Processing airthings data: {value}, name: {name}");
                    await HandleAirthingsData(name, value, conn, token);
                }

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

    private async Task HandleAirthingsData(string name, string value, NpgsqlConnection conn, CancellationToken token)
    {
        try
        {
            using var doc = JsonDocument.Parse(value);
            var root = doc.RootElement;
 
            string pin = "";

            double temperature = root.GetProperty("temperature").GetDouble();
            double humidity = root.GetProperty("humidity").GetDouble();
            double co2 = root.GetProperty("co2").GetDouble();
            double voc = root.GetProperty("voc").GetDouble();
            double pm25 = root.GetProperty("pm25").GetDouble();
            double radon = root.GetProperty("radon").GetDouble();
            double pressure = root.GetProperty("pressure").GetDouble();

            const string insertSql = @"
                INSERT INTO airthings (
                    name, pin, temperature, humidity, co2, voc, pm25, radon, pressure, raw_data
                ) VALUES (
                    @name, @pin, @temperature, @humidity, @co2, @voc, @pm25, @radon, @pressure, @raw_data
                );
            ";
            using var cmd = new NpgsqlCommand(insertSql, conn);
            cmd.Parameters.AddWithValue("name", name);
            cmd.Parameters.AddWithValue("pin", pin);
            cmd.Parameters.AddWithValue("temperature", temperature);
            cmd.Parameters.AddWithValue("humidity", humidity);
            cmd.Parameters.AddWithValue("co2", co2);
            cmd.Parameters.AddWithValue("voc", voc);
            cmd.Parameters.AddWithValue("pm25", pm25);
            cmd.Parameters.AddWithValue("radon", radon);
            cmd.Parameters.AddWithValue("pressure", pressure);
            cmd.Parameters.AddWithValue("raw_data", NpgsqlTypes.NpgsqlDbType.Jsonb, value); // value is the original JSON string

            await cmd.ExecuteNonQueryAsync(token);
        }
        catch (Exception ex)
        {
            logger.LogError($"Error processing Airthings data: {ex.Message}");
            return;
        }

    }
}