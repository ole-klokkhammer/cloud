using System.Collections.Generic;
using System.Text.Json.Serialization;

public class GattRoot
{
    [JsonPropertyName("services")]
    public Dictionary<string, GattService> Services { get; set; }
}

public class GattService
{
    [JsonPropertyName("description")]
    public string Description { get; set; }

    [JsonPropertyName("characteristics")]
    public Dictionary<string, GattCharacteristic> Characteristics { get; set; }
}

public class GattCharacteristic
{
    [JsonPropertyName("description")]
    public string Description { get; set; }

    [JsonPropertyName("properties")]
    public List<string> Properties { get; set; }

    [JsonPropertyName("value")]
    public GattValue Value { get; set; }

    [JsonPropertyName("error")]
    public string Error { get; set; }

    [JsonPropertyName("descriptors")]
    public Dictionary<string, GattDescriptor> Descriptors { get; set; }
}

public class GattDescriptor
{
    [JsonPropertyName("description")]
    public string Description { get; set; }

    [JsonPropertyName("value")]
    public GattValue Value { get; set; }

    [JsonPropertyName("error")]
    public string Error { get; set; }
}

public class GattValue
{
    [JsonPropertyName("hex")]
    public string Hex { get; set; }

    [JsonPropertyName("utf8")]
    public string Utf8 { get; set; }
}