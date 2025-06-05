using Microsoft.Extensions.Logging;

public class AirthingsRepository
{
    private readonly ILogger<AirthingsRepository> logger;
    private readonly PostgresService postgresService;

    public AirthingsRepository(
        ILogger<AirthingsRepository> logger,
        PostgresService postgresService
    )
    {
        this.postgresService = postgresService;
        this.logger = logger;
    }

    public async Task<int?> GetSerialByMacAsync(string mac)
    {
        var result = await postgresService.GetDataAsync<int?>(
            @"
                SELECT serial 
                FROM bluetooth.airthings_device
                WHERE mac = @mac
                ORDER BY timestamp DESC
                LIMIT 1;
            ",
            new Dictionary<string, object>
            {
                { "mac", mac }
            }
        );
        return result?.FirstOrDefault();
    }

    public async Task InsertBatteryDataAsync(AirthingsBatteryData airthingsBatteryData)
    {
        await postgresService.InsertDataAsync(
            @$"
                INSERT INTO bluetooth.airthings_battery (
                    serial, battery_level, voltage
                ) VALUES (
                    @serial, @battery_level, @voltage
                );
            ",
            new Dictionary<string, object>
            {
                { "serial", airthingsBatteryData.Serial },
                { "battery_level", airthingsBatteryData.BatteryLevel },
                { "voltage", airthingsBatteryData.Voltage }
            }
        );
    }

    public async Task InsertSensorDataAsync(AirthingsSensorData sensorData)
    {
        await postgresService.InsertDataAsync(
            @$"  
                INSERT INTO bluetooth.airthings_data (
                    serial, temperature, humidity, co2, voc, radon_1_day_average, radon_long_term_average, pressure
                ) VALUES (
                    @serial, @temperature, @humidity, @co2, @voc, @radon_1_day_average, @radon_long_term_average, @pressure
                );
            ",
            new Dictionary<string, object>
            {
                { "serial", sensorData.Serial },
                { "temperature", sensorData.Temperature ?? (object)DBNull.Value },
                { "humidity", sensorData.Humidity ?? (object)DBNull.Value },
                { "co2", sensorData.CO2 ?? (object)DBNull.Value },
                { "voc", sensorData.VOC ?? (object)DBNull.Value },
                { "pressure", sensorData.Pressure ?? (object)DBNull.Value },
                { "illuminance", sensorData.Illuminance ?? (object)DBNull.Value },
                { "radon_1_day_average", sensorData.Radon1DayAverage ?? (object)DBNull.Value },
                { "radon_long_term_average", sensorData.RadonLongTermAverage ?? (object)DBNull.Value }
            }
        );
    }

    public async Task InsertDeviceAsync(AirthingsDevice airthingsDevice)
    {
        await postgresService.InsertDataAsync(
            @$"
                INSERT INTO bluetooth.airthings_device (
                    serial, model_number, mac, manufacturer_name, hardware_revision, firmware_revision, location_id
                ) VALUES (
                    @serial, @model_number, @mac, @manufacturer_name, @hardware_revision, @firmware_revision, @location_id
                );
            ",
            new Dictionary<string, object>
            {
                { "serial", airthingsDevice.Serial },
                { "model_number", airthingsDevice.ModelNumber },
                { "mac", airthingsDevice.Mac },
                { "manufacturer_name", airthingsDevice.ManufacturerName ?? (object)DBNull.Value },
                { "hardware_revision", airthingsDevice.HardwareRevision ?? (object)DBNull.Value },
                { "firmware_revision", airthingsDevice.FirmwareRevision ?? (object)DBNull.Value },
                { "location_id", airthingsDevice.LocationId ?? (object)DBNull.Value }
            }
        );
    }
}