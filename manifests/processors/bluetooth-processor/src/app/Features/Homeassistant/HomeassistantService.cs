using Microsoft.Extensions.Logging;

public class HomeassistantService(
    JsonUtil json,
    ILogger<HomeassistantService> logger,
    RabbitMqService rabbitMqService
)
{


    // FIXME this is a temporary solution, we should maybe do this manually or smth instead
    public async Task<bool> TryUpdateAirthingsHomeAssistantAutoDiscovery(int serial)
    {
        try
        {
            string location = MapSerialToRoom(serial); // TODO consider asking the db in the future
            var configs = new List<(string Key, string Topic, object Payload)>
        {
            ("humidity", $"homeassistant/sensor/airthings_{location}/humidity/config", new {
                platform = "sensor",
                name = $"{location.Capitalize()} Humidity",
                unit_of_measurement = "%",
                state_topic = $"bluetooth/airthings/{serial}/data",
                value_template = "{{ value_json.humidity }}",
                device_class = "humidity"
            }),
            ("illuminance", $"homeassistant/sensor/airthings_{location}/illuminance/config", new {
                platform = "sensor",
                name = $"{location.Capitalize()} Illuminance",
                unit_of_measurement = "lx",
                state_topic = $"bluetooth/airthings/{serial}/data",
                value_template = "{{ value_json.illuminance }}",
                device_class = "illuminance"
            }),
            ("radon_1day_avg", $"homeassistant/sensor/airthings_{location}/radon_1day_avg/config", new {
                platform = "sensor",
                name = $"{location.Capitalize()} Radon 1 Day Avg",
                unit_of_measurement = "Bq/m³",
                state_topic = $"bluetooth/airthings/{serial}/data",
                value_template = "{{ value_json.radon1DayAverage }}",
                icon = "mdi:radioactive"
            }),
            ("radon_longterm_avg", $"homeassistant/sensor/airthings_{location}/radon_longterm_avg/config", new {
                platform = "sensor",
                name = $"{location.Capitalize()} Radon Longterm Avg",
                unit_of_measurement = "Bq/m³",
                state_topic = $"bluetooth/airthings/{serial}/data",
                value_template = "{{ value_json.radonLongTermAverage }}",
                icon = "mdi:radioactive"
            }),
            ("temperature", $"homeassistant/sensor/airthings_{location}/temperature/config", new {
                platform = "sensor",
                name = $"{location.Capitalize()} Temperature",
                unit_of_measurement = "°C",
                state_topic = $"bluetooth/airthings/{serial}/data",
                value_template = "{{ value_json.temperature }}",
                device_class = "temperature"
            }),
            ("pressure", $"homeassistant/sensor/airthings_{location}/pressure/config", new {
                platform = "sensor",
                name = $"{location.Capitalize()} Pressure",
                unit_of_measurement = "hPa",
                state_topic = $"bluetooth/airthings/{serial}/data",
                value_template = "{{ value_json.pressure }}",
                device_class = "pressure"
            }),
            ("co2", $"homeassistant/sensor/airthings_{location}/co2/config", new {
                platform = "sensor",
                name = $"{location.Capitalize()} CO2",
                unit_of_measurement = "ppm",
                state_topic = $"bluetooth/airthings/{serial}/data",
                value_template = "{{ value_json.co2 }}",
                device_class = "carbon_dioxide"
            }),
            ("voc", $"homeassistant/sensor/airthings_{location}/voc/config", new {
                platform = "sensor",
                name = $"{location.Capitalize()} VOC",
                unit_of_measurement = "ppb",
                state_topic = $"bluetooth/airthings/{serial}/data",
                value_template = "{{ value_json.voc }}",
                icon = "mdi:chemical-weapon"
            })
        };

            foreach (var (key, topic, payload) in configs)
            {
                await rabbitMqService.PublishMqttAsync(topic, json.Serialize(payload));
            }
            return true;
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "Failed to publish Airthings sensor configs");
            return false;
        }
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
