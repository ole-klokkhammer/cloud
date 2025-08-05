using Microsoft.Extensions.Logging;

public class HomeassistantService(
    JsonUtil json,
    ILogger<HomeassistantService> logger,
    RabbitMqService rabbitMqService
)
{

    public async Task<bool> TryHomeAssistantAutoDiscoveryAirthingsSensor(AirthingsSensor sensor)
    {
        try
        {
            var serial = sensor.DeviceInfo.Serial;

            object device = new
            {
                identifiers = new[] { $"airthings_wave_plus{serial}" },
                name = $"Airthings Wave Plus {serial}",
                manufacturer = "Airthings",
                model = "Wave Plus",
                model_id = $"airthings_{serial}",
                via_device = "bluetooth"
            };

            object origin = new
            {
                name = "BluetoothPostprocessor",
                sw = "1.0.0",
                url = "https://github.com/oleklokkhammer/bluetooth-postprocessor"
            };

            var configs = new List<(string Key, string Topic, object Payload)>
            {
                ("humidity", $"homeassistant/sensor/airthings_wave_plus_{serial}/humidity/config", new {
                    device,
                    device_class = "humidity",
                    enabled_by_default = true,
                    object_id = $"airthings_{serial}_humidity",
                    origin,
                    state_class = "measurement",
                    state_topic = $"bluetooth/airthings/{serial}/data",
                    unique_id = $"airthings_{serial}_humidity_bluetooth",
                    unit_of_measurement = "%",
                    value_template = "{{ value_json.humidity }}"
                }),
                ("illuminance", $"homeassistant/sensor/airthings_wave_plus_{serial}/illuminance/config", new {
                    device,
                    device_class = "illuminance",
                    enabled_by_default = true,
                    object_id = $"airthings_{serial}_illuminance",
                    origin,
                    state_class = "measurement",
                    state_topic = $"bluetooth/airthings/{serial}/data",
                    unique_id = $"airthings_{serial}_illuminance_bluetooth",
                    unit_of_measurement = "lx",
                    value_template = "{{ value_json.illuminance }}"
                }),
                ("radon_1day_avg", $"homeassistant/sensor/airthings_wave_plus_{serial}/radon_1day_avg/config", new {
                    device,
                    enabled_by_default = true,
                    object_id = $"airthings_{serial}_radon_1day_avg",
                    origin,
                    state_class = "measurement",
                    state_topic = $"bluetooth/airthings/{serial}/data",
                    unique_id = $"airthings_{serial}_radon_1day_avg_bluetooth",
                    unit_of_measurement = "Bq/m³",
                    value_template = "{{ value_json.radon1DayAverage }}",
                    icon = "mdi:radioactive"
                }),
                ("radon_longterm_avg", $"homeassistant/sensor/airthings_wave_plus_{serial}/radon_longterm_avg/config", new {
                    device,
                    enabled_by_default = true,
                    object_id = $"airthings_{serial}_radon_longterm_avg",
                    origin,
                    state_class = "measurement",
                    state_topic = $"bluetooth/airthings/{serial}/data",
                    unique_id = $"airthings_{serial}_radon_longterm_avg_bluetooth",
                    unit_of_measurement = "Bq/m³",
                    value_template = "{{ value_json.radonLongTermAverage }}",
                    icon = "mdi:radioactive"
                }),
                ("temperature", $"homeassistant/sensor/airthings_wave_plus_{serial}/temperature/config", new {
                    device,
                    device_class = "temperature",
                    enabled_by_default = true,
                    object_id = $"airthings_{serial}_temperature",
                    origin,
                    state_class = "measurement",
                    state_topic = $"bluetooth/airthings/{serial}/data",
                    unique_id = $"airthings_{serial}_temperature_bluetooth",
                    unit_of_measurement = "°C",
                    value_template = "{{ value_json.temperature }}"
                }),
                ("pressure", $"homeassistant/sensor/airthings_wave_plus_{serial}/pressure/config", new {
                    device,
                    device_class = "pressure",
                    enabled_by_default = true,
                    object_id = $"airthings_{serial}_pressure",
                    origin,
                    state_class = "measurement",
                    state_topic = $"bluetooth/airthings/{serial}/data",
                    unique_id = $"airthings_{serial}_pressure_bluetooth",
                    unit_of_measurement = "hPa",
                    value_template = "{{ value_json.pressure }}"
                }),
                ("co2", $"homeassistant/sensor/airthings_wave_plus_{serial}/co2/config", new {
                    device,
                    device_class = "carbon_dioxide",
                    enabled_by_default = true,
                    object_id = $"airthings_{serial}_co2",
                    origin,
                    state_class = "measurement",
                    state_topic = $"bluetooth/airthings/{serial}/data",
                    unique_id = $"airthings_{serial}_co2_bluetooth",
                    unit_of_measurement = "ppm",
                    value_template = "{{ value_json.co2 }}"
                }),
                ("voc", $"homeassistant/sensor/airthings_wave_plus_{serial}/voc/config", new {
                    device,
                    enabled_by_default = true,
                    object_id = $"airthings_{serial}_voc",
                    origin,
                    state_class = "measurement",
                    state_topic = $"bluetooth/airthings/{serial}/data",
                    unique_id = $"airthings_{serial}_voc_bluetooth",
                    unit_of_measurement = "ppb",
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