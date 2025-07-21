using System.Data;
using Microsoft.Extensions.Logging;
using Npgsql;

public class PostgresService
{
    private readonly ILogger<PostgresService> logger;
    private readonly string connectionString;

    private NpgsqlDataSource dataSource = null!;

    public PostgresService(ILogger<PostgresService> logger)
    {
        this.logger = logger;
        this.connectionString = @$"
            Host={AppEnvironment.DbHost};
            Port={AppEnvironment.DbPort};
            Username={AppEnvironment.DbUser};
            Password={AppEnvironment.DbPassword};
            Database={AppEnvironment.DbName}
        ";
    }

    public void Initialize()
    {
        logger.LogInformation("Creating PostgreSQL datasource...");
        dataSource = NpgsqlDataSource.Create(connectionString);
        logger.LogInformation("PostgreSQL datasource created.");
    }

    public async Task Shutdown()
    {
        logger.LogInformation("Disposing PostgreSQL data source...");
        if (dataSource != null)
            await dataSource.DisposeAsync();
    }

    public async Task<List<T>> GetDataAsync<T>(string commandString, Dictionary<string, object> parameters)
    {
        await using var conn = dataSource.CreateConnection();
        await conn.OpenAsync();
        await using var cmd = new NpgsqlCommand(commandString, conn);

        foreach (var kvp in parameters)
        {
            if (kvp.Value is NpgsqlParameter param)
            {
                cmd.Parameters.Add(param);
            }
            else
            {
                cmd.Parameters.AddWithValue(kvp.Key, kvp.Value);
            }
        }

        var results = new List<T>();
        await using var reader = await cmd.ExecuteReaderAsync();
        while (await reader.ReadAsync())
        {
            
            results.Add(reader.GetFieldValue<T>(0)); // Assuming single column result
        }
        return results;
    }

    public async Task InsertDataAsync(string command, Dictionary<string, object> data)
    {
        await using var conn = dataSource.CreateConnection();
        await conn.OpenAsync();
        await using var cmd = new NpgsqlCommand(command, conn);
        foreach (var kvp in data)
        {
            if (kvp.Value is NpgsqlParameter param)
            {
                cmd.Parameters.Add(param);
            }
            else
            {
                cmd.Parameters.AddWithValue(kvp.Key, kvp.Value);
            }
        }
        await cmd.ExecuteNonQueryAsync();
    }
}