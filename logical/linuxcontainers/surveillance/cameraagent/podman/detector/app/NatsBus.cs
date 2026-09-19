// NATS events: one "detection_burst" event per closed burst.
// Stills on disk are the source of truth; events are fire-and-forget - if the bus
// is down, stills are still written and the embedder is unaffected.
using System.Text.Json;
using NATS.Client.Core;
using NATS.Net;

namespace Detector;

internal sealed record BestFrame(string File, string Path, double Confidence, string FrameTs, int[] Box);

internal sealed record DetectionEvent
{
    [System.Text.Json.Serialization.JsonPropertyName("event")] public string Event { get; init; } = "detection_burst";
    [System.Text.Json.Serialization.JsonPropertyName("camera")] public string Camera { get; init; } = "";
    [System.Text.Json.Serialization.JsonPropertyName("label")] public string Label { get; init; } = "";
    [System.Text.Json.Serialization.JsonPropertyName("ts")] public string Ts { get; init; } = "";
    [System.Text.Json.Serialization.JsonPropertyName("detections")] public int Detections { get; init; }
    [System.Text.Json.Serialization.JsonPropertyName("best")] public BestFrame Best { get; init; } = null!;
    [System.Text.Json.Serialization.JsonPropertyName("detector")] public string Detector { get; init; } = "detector.net/1.0";
}

internal sealed class NatsBus
{
    private readonly string _url;
    private readonly string _subject;
    private readonly JsonSerializerOptions _json = new();
    private NatsClient? _client;
    private DateTime _lastTry;

    public NatsBus(string url, string subject) { _url = url; _subject = subject; }

    /// <summary>Initial connect; on failure the service runs still-only until reconnection.</summary>
    public async Task ConnectAsync()
    {
        try
        {
            _client = new NatsClient(new NatsOpts { Url = _url });
            await _client.ConnectAsync();
            Log.Info($"nats connected: {_url}");
        }
        catch (Exception e)
        {
            Log.Info($"nats unavailable ({e.Message}); stills still written, events skipped until it's back");
            _client = null;
        }
    }

    /// <summary>Emit the burst event (journal + NATS). Lazy-reconnects after 10 s; drops on failure.</summary>
    public async Task PublishBurstAsync(string camera, string stillFile, Candidate best,
        int detectionFrames, double scale, double ox, double oy)
    {
        var evt = new DetectionEvent
        {
            Camera = camera,
            Label = Labels.For(best.Det.ClassId),
            Ts = DateTime.Now.ToString("o"),
            Detections = detectionFrames,
            Best = new BestFrame(
                Path.GetFileName(stillFile),
                stillFile,
                Math.Round(best.Conf, 3),
                best.Ts.ToString("o"),
                new[] {
                    (int)YoloModel.Unmap(best.Det.X1, scale, ox),
                    (int)YoloModel.Unmap(best.Det.Y1, scale, oy),
                    (int)YoloModel.Unmap(best.Det.X2, scale, ox),
                    (int)YoloModel.Unmap(best.Det.Y2, scale, oy) }),
        };
        Log.Json(evt);
        var payload = JsonSerializer.SerializeToUtf8Bytes(evt, _json);

        if (_client is null && DateTime.Now - _lastTry > TimeSpan.FromSeconds(10))
        {
            _lastTry = DateTime.Now;
            try
            {
                _client = new NatsClient(new NatsOpts { Url = _url });
                await _client.ConnectAsync();
                Log.Info($"nats reconnected: {_url}");
            }
            catch { return; }
        }
        if (_client is null) return;
        try
        {
            await _client.PublishAsync(_subject, payload);
        }
        catch (Exception e)
        {
            Log.Info($"nats publish failed: {e.Message}");
            try { await _client.DisposeAsync(); } catch { }
            _client = null;
        }
    }

    public async ValueTask DisposeAsync()
    {
        if (_client is not null) await _client.DisposeAsync();
    }
}
