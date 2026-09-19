// Console logging: plain lines + one-line JSON events (the journal is the audit log).
using System.Text.Json;

namespace Detector;

internal static class Log
{
    private static readonly JsonSerializerOptions Opts = new();

    public static void Info(string msg) => Console.WriteLine($"[detector] {msg}");

    public static void Json(object o) => Console.WriteLine(JsonSerializer.Serialize(o, Opts));
}
