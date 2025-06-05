using Microsoft.Extensions.Logging;

class HomeassistantService
{
    private readonly ILogger<HomeassistantService> logger;
    private readonly MqttService mqttService;


    public HomeassistantService(
        ILogger<HomeassistantService> logger,
        MqttService mqttService
    )
    {
        this.logger = logger;
        this.mqttService = mqttService;
    }

    public async Task<bool> TryPublishAirthingsSensorConfigsAsync(
        int serial,
        AirthingsSensorData sensorData
    )
    {
        try
        {
            string location = MapSerialToRoom(serial); // TODO consider asking the db in the future
            var configs = new List<(string Key, string Topic, object Payload)>
        {
            ("humidity", $"homeassistant/sensor/airthings_{location}_humidity/config", new {
                name = $"{Capitalize(location)} Humidity",
                state_topic = $"bluetooth/airthings/{serial}/sensor",
                unit_of_measurement = "%",
                value_template = sensorData.Humidity,
                device_class = "humidity"
            }),
            ("illuminance", $"homeassistant/sensor/airthings_{location}_illuminance/config", new {
                name = $"{Capitalize(location)} Illuminance",
                state_topic = $"bluetooth/airthings/{serial}/sensor",
                unit_of_measurement = "lx",
                value_template = sensorData.Illuminance,
                device_class = "illuminance"
            }),
            ("radon_1day_avg", $"homeassistant/sensor/airthings_{location}_radon_1day_avg/config", new {
                name = $"{Capitalize(location)} Radon 1 Day Avg",
                state_topic = $"bluetooth/airthings/{serial}/sensor",
                unit_of_measurement = "Bq/m³",
                value_template =sensorData.Radon1DayAverage,
                icon = "mdi:radioactive"
            }),
            ("radon_longterm_avg", $"homeassistant/sensor/airthings_{location}_radon_longterm_avg/config", new {
                name = $"{Capitalize(location)} Radon Longterm Avg",
                state_topic = $"bluetooth/airthings/{serial}/sensor",
                unit_of_measurement = "Bq/m³",
                value_template = sensorData.RadonLongTermAverage,
                icon = "mdi:radioactive"
            }),
            ("temperature", $"homeassistant/sensor/airthings_{location}_temperature/config", new {
                name = $"{Capitalize(location)} Temperature",
                state_topic = $"bluetooth/airthings/{serial}/sensor",
                unit_of_measurement = "°C",
                value_template = sensorData.Temperature,
                device_class = "temperature"
            }),
            ("pressure", $"homeassistant/sensor/airthings_{location}_pressure/config", new {
                name = $"{Capitalize(location)} Pressure",
                state_topic = $"bluetooth/airthings/{serial}/sensor",
                unit_of_measurement = "hPa",
                value_template = sensorData.Pressure,
                device_class = "pressure"
            }),
            ("co2", $"homeassistant/sensor/airthings_{location}_co2/config", new {
                name = $"{Capitalize(location)} CO2",
                state_topic = $"bluetooth/airthings/{serial}/sensor",
                unit_of_measurement = "ppm",
                value_template = sensorData.CO2,
                device_class = "carbon_dioxide"
            }),
            ("voc", $"homeassistant/sensor/airthings_{location}_voc/config", new {
                name = $"{Capitalize(location)} VOC",
                state_topic = $"bluetooth/airthings/{serial}/sensor",
                unit_of_measurement = "ppb",
                value_template = sensorData.VOC,
                icon = "mdi:chemical-weapon"
            })
        };

            foreach (var (key, topic, payload) in configs)
            {
                await mqttService.TryPublishAsync(topic, payload);
            }
            return true;
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "Failed to publish Airthings sensor configs");
            return false;
        }
    }

    private string Capitalize(string input)
    {
        if (string.IsNullOrEmpty(input)) return input;
        return char.ToUpper(input[0]) + input.Substring(1);
    }

    private string MapSerialToRoom(int serial)
    {
        return serial switch
        {
            151076 => "basement",
            18919 => "bedroom",
            145104 => "livingroom",
            _ => "unknown_location"
        };
    }
}