using System.Text.Json;

public class JsonUtil
{
    private readonly JsonSerializerOptions options;

    public JsonUtil()
    {
        options = new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
            WriteIndented = false
        };
    }

    public string Serialize<T>(T obj) =>
        JsonSerializer.Serialize(obj, options);

    public T? Deserialize<T>(string json) =>
        JsonSerializer.Deserialize<T>(json, options);
}