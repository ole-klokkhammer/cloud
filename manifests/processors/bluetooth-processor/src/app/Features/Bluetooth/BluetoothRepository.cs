using System.Text.Json;

public class BluetoothRepository
{
    private readonly PostgresService postgresService;
    private readonly JsonUtil json;

    public BluetoothRepository(
        PostgresService postgresService,
        JsonUtil json
    )
    {
        this.postgresService = postgresService;
        this.json = json;
    }


    public async Task InsertScanAsync(BluetoothScan scan)
    {
        await postgresService.InsertDataAsync(
            @$"
                    INSERT INTO bluetooth.scan (
                        name, address, rssi, manufacturer_data
                    ) VALUES (
                        @name, @address, @rssi, @manufacturer_data
                    );
                ",
            new Dictionary<string, object>
            {
                    { "name", scan.name ?? (object)DBNull.Value },
                    { "address", scan.address ?? (object)DBNull.Value },
                    { "rssi", scan.rssi },
                    { "manufacturer_data", new Npgsql.NpgsqlParameter
                        {
                            ParameterName = "manufacturer_data",
                            NpgsqlDbType = NpgsqlTypes.NpgsqlDbType.Jsonb,
                            Value = scan.manufacturer_data != null ?
                                json.Serialize(scan.manufacturer_data)
                                : "{}"
                        }
                    }
            }
        );
    }
}