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

    public async Task<List<string>> GetDataAsync(string command)
    {
        var result = new List<string>();
        await using var conn = dataSource.CreateConnection();
        await using (var cmd = new NpgsqlCommand(command, conn))
        await using (var reader = await cmd.ExecuteReaderAsync())
        {
            while (await reader.ReadAsync())
            {
                result.Add(reader.GetString(0));
            }
        }

        return result;
    }

    public async Task InsertDataAsync(string command, Dictionary<string, object> data)
    {
        await using var conn = dataSource.CreateConnection();
        await using var cmd = new NpgsqlCommand(command, conn);
        foreach (var kvp in data)
        {
            cmd.Parameters.AddWithValue(kvp.Key, kvp.Value);
        }
        await cmd.ExecuteNonQueryAsync();
    }

    public async Task InsertDataTransactional(string command, Dictionary<string, string> data)
    {
        await using var conn = dataSource.CreateConnection();
        await using var transaction = await conn.BeginTransactionAsync();
        try
        {
            await using var cmd = new NpgsqlCommand(command, conn, transaction);
            foreach (var kvp in data)
            {
                cmd.Parameters.AddWithValue(kvp.Key, kvp.Value);
            }
            await cmd.ExecuteNonQueryAsync();
            await transaction.CommitAsync();
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "Failed to insert data into PostgreSQL database.");
            await transaction.RollbackAsync();
            throw;
        }
    }
}