using System.Text.Json;
using Confluent.Kafka;
using Microsoft.Extensions.Logging;
using Npgsql;

class AirthingsService
{
    private readonly ILogger<AirthingsService> logger;

    private static readonly string ServicesSensorDataServiceUuid = "b42e1c08-ade7-11e4-89d3-123b93f75cba";
    private static readonly string CharacteristicCurrentSensorValuesUuid = "b42e2a68-ade7-11e4-89d3-123b93f75cba";

    public AirthingsService(ILogger<AirthingsService> logger)
    {
        this.logger = logger;
    }

    public async Task HandleConnectPayload(string payload)
    {
        var data = JsonSerializer.Deserialize<GattRoot>(payload);
        if (data == null)
        {
            logger.LogWarning("No data found in payload.");
            return;
        }

        var service = data.Services.FirstOrDefault(s => s.Key == ServicesSensorDataServiceUuid);
        if (service.Value == null)
        {
            logger.LogWarning("Service not found in data.");
            return;
        }

        var characteristic = service.Value.Characteristics.FirstOrDefault(c => c.Key == CharacteristicCurrentSensorValuesUuid);
        if (characteristic.Value == null)
        {
            logger.LogWarning("Characteristic not found in service.");
            return;
        }

        var hexValue = characteristic.Value.Value.Hex;
        var byteArray = HexUtils.ToByteArray(hexValue);
        var value = ByteUtils.Unpack4B8H(byteArray);
        var humidity = value[1] / 2.0;
        var illuminance = (int)(value[2] / 255.0 * 100);
        var radon_1day_avg = value[4];
        var radon_longterm_avg = value[5];
        var temperature = value[6] / 100.0;
        var pressure = value[7] / 50.0;
        var co2 = value[8] * 1.0;
        var voc = value[9] * 1.0;

        logger.LogInformation($"Humidity: {humidity}%");
        logger.LogInformation($"Illuminance: {illuminance}%");
        logger.LogInformation($"Radon 1-day average: {radon_1day_avg} Bq/m³");
        logger.LogInformation($"Radon long-term average: {radon_longterm_avg} Bq/m³");
        logger.LogInformation($"Temperature: {temperature} °C");
        logger.LogInformation($"Pressure: {pressure} hPa");
        logger.LogInformation($"CO2: {co2} ppm");
        logger.LogInformation($"VOC: {voc} ppb");

    }

}



// async def read_wave_plus_read_sensor_data(address: str) -> Optional[SensorData]:
//     response = await device.connect(address = address)
//     service = response.services["b42e1c08-ade7-11e4-89d3-123b93f75cba"]
//     characteristic = service.characteristics["b42e2a68-ade7-11e4-89d3-123b93f75cba"]
//     return parse_wave_plus_sensor_data(bytearray.fromhex(characteristic.value.hex))
