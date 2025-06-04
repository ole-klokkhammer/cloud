using System.Text.Json;
using Microsoft.Extensions.Logging;
using Npgsql;

class AirthingsService
{
    private readonly ILogger<AirthingsService> logger;
    private readonly PostgresService postgresService;

    public AirthingsService(
        ILogger<AirthingsService> logger,
        PostgresService postgresService
    )
    {
        this.logger = logger;
        this.postgresService = postgresService;
    }

    public async Task HandleCommandPayload(string kafkaKey, byte[] payload)
    {
        logger.LogInformation($"Received command payload for key: {kafkaKey}");
        logger.LogInformation($"Payload: {payload}");

        var cmd = payload.Take(1).ToArray();

        var data = ByteUtils.UnpackL2BH2B9H(payload.Skip(2).ToArray());
        float batteryVolt = (float)((ushort)data[13] / 1000.0);
        logger.LogInformation($"Battery voltage: {batteryVolt}V");

        int batteryLevel = BatteryPercentage(batteryVolt);
        logger.LogInformation($"Battery percentage: {batteryLevel}%");

        var mac = kafkaKey.Split('/')[2];
        var serialResult = await postgresService.GetDataAsync<int?>(
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

        if (serialResult == null || serialResult.Count == 0)
        {
            throw new ArgumentException($"No device found for kafkaKey: {kafkaKey}");
        }

        var serial = serialResult[0]!;
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
                { "serial", serial },
                { "battery_level", batteryLevel },
                { "voltage", batteryVolt }
            }
        );
    }

    public async Task HandleConnectPayload(string kafkaKey, string payload)
    {
        var data = JsonSerializer.Deserialize<GattRoot>(payload);
        if (data == null)
        {
            logger.LogWarning("No data found in payload.");
            return;
        }

        var mac = kafkaKey.Split('/').LastOrDefault();
        if (string.IsNullOrEmpty(mac))
        {
            throw new ArgumentException("MAC address not found in Kafka key.");
        }

        var airthingsDevice = ParseDeviceInfo(data, mac);
        if (airthingsDevice == null)
        {
            throw new ArgumentException("Airthings device info not found in data.");
        }

        logger.LogDebug($"Airthings device found: {airthingsDevice.Serial} - {airthingsDevice.ModelNumber} - {airthingsDevice.Mac}");
        logger.LogDebug("Inserting Airthings device into database...");
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

        var airthingsSensorData = ParseSensorData(data, airthingsDevice!.Serial, airthingsDevice.LocationId);
        if (airthingsSensorData == null)
        {
            throw new ArgumentException("Airthings sensor data not found in data.");
        }

        logger.LogDebug($"Airthings sensor data found: {airthingsSensorData.Serial} - {airthingsSensorData.Temperature} - {airthingsSensorData.Humidity}");
        logger.LogDebug("Inserting Airthings sensor data into database...");
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
                { "serial", airthingsSensorData.Serial },
                { "temperature", airthingsSensorData.Temperature ?? (object)DBNull.Value },
                { "humidity", airthingsSensorData.Humidity ?? (object)DBNull.Value },
                { "co2", airthingsSensorData.CO2 ?? (object)DBNull.Value },
                { "voc", airthingsSensorData.VOC ?? (object)DBNull.Value },
                { "pressure", airthingsSensorData.Pressure ?? (object)DBNull.Value },
                { "illuminance", airthingsSensorData.Illuminance ?? (object)DBNull.Value },
                { "radon_1_day_average", airthingsSensorData.Radon1DayAverage ?? (object)DBNull.Value },
                { "radon_long_term_average", airthingsSensorData.RadonLongTermAverage ?? (object)DBNull.Value }
            }
        );
    }

    private AirthingsSensorData? ParseSensorData(GattRoot data, int serial, string? LocationId)
    {
        var service = data.Services.FirstOrDefault(s => s.Key == AirthingsUuids.Services.SensorData);
        if (service.Value == null)
        {
            logger.LogWarning("Service not found in data.");
            return null;
        }

        var characteristic = service.Value.Characteristics.FirstOrDefault(c => c.Key == AirthingsUuids.Characteristics.CurrentSensorValue);
        if (characteristic.Value == null)
        {
            logger.LogWarning("Characteristic not found in service.");
            return null;
        }

        var hexValue = characteristic.Value.Value.Hex;
        var byteArray = HexUtils.ToByteArray(hexValue);
        var value = ByteUtils.Unpack4B8H(byteArray);

        return new AirthingsSensorData
        {
            Serial = serial,
            LocationId = LocationId,
            Humidity = value[1] / 2.0,
            Illuminance = (int)(value[2] / 255.0 * 100),
            Radon1DayAverage = value[4],
            RadonLongTermAverage = value[5],
            Temperature = value[6] / 100.0,
            Pressure = value[7] / 50.0,
            CO2 = value[8] * 1.0,
            VOC = value[9] * 1.0
        };
    }

    private AirthingsDevice? ParseDeviceInfo(GattRoot data, string mac)
    {
        var service = data.Services.FirstOrDefault(s => s.Key == AirthingsUuids.Services.DeviceInfo);
        if (service.Value == null)
        {
            logger.LogWarning("Service not found in data.");
            return null;
        }

        var systemId = service.GetCharacteristicValue(AirthingsUuids.Characteristics.DeviceInfo.SystemId);
        var hardwareRevision = service.GetCharacteristicValue(AirthingsUuids.Characteristics.DeviceInfo.HardwareRevision);
        var serial = service.GetCharacteristicValue(AirthingsUuids.Characteristics.DeviceInfo.SerialNumber);
        var modelNumber = service.GetCharacteristicValue(AirthingsUuids.Characteristics.DeviceInfo.ModelNumber);
        var manufacturerName = service.GetCharacteristicValue(AirthingsUuids.Characteristics.DeviceInfo.ManufacturerName);
        var firmwareRevision = service.GetCharacteristicValue(AirthingsUuids.Characteristics.DeviceInfo.FirmwareRevision);

        return new AirthingsDevice
        {
            Serial = int.Parse(serial!),
            ModelNumber = int.Parse(modelNumber!),
            Mac = mac!,
            ManufacturerName = manufacturerName!,
            HardwareRevision = hardwareRevision!,
            FirmwareRevision = firmwareRevision!,
            LocationId = null
        };
    }

    public static int BatteryPercentage(float voltage)
    {
        return (int)Math.Round(TwoBatteries(voltage));
    }

    private static float TwoBatteries(float voltage)
    {
        if (voltage >= 3.00f)
            return 100;
        if (voltage >= 2.80f && voltage < 3.00f)
            return Interpolate(voltage, (2.80f, 3.00f), (81, 100));
        if (voltage >= 2.60f && voltage < 2.80f)
            return Interpolate(voltage, (2.60f, 2.80f), (53, 81));
        if (voltage >= 2.50f && voltage < 2.60f)
            return Interpolate(voltage, (2.50f, 2.60f), (28, 53));
        if (voltage >= 2.20f && voltage < 2.50f)
            return Interpolate(voltage, (2.20f, 2.50f), (5, 28));
        if (voltage >= 2.10f && voltage < 2.20f)
            return Interpolate(voltage, (2.10f, 2.20f), (0, 5));
        return 0;
    }

    private static float Interpolate(float voltage, (float, float) voltageRange, (int, int) percentageRange)
    {
        return (voltage - voltageRange.Item1) / (voltageRange.Item2 - voltageRange.Item1) *
               (percentageRange.Item2 - percentageRange.Item1) + percentageRange.Item1;
    }
}

