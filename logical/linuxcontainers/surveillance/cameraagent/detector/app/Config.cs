// Service configuration: every knob is an env var (see podman/detector.env.example).
namespace Detector;

internal sealed class DetectorOptions
{
    public string RtspUrl { get; }
    public string ModelPath { get; }
    public string EventDir { get; }
    public string Camera { get; }
    public string Device { get; }        // "cuda" | "cpu"
    public int InputSize { get; }       // must match the export's imgsz
    public int FrameWidth { get; }      // decode width = still resolution
    public double MinConf { get; }
    public double BurstWindowSecs { get; }
    public double MaxFps { get; }
    public string NatsUrl { get; }
    public string NatsSubject { get; }
    public HashSet<int> Classes { get; }

    /// <summary>Seconds between inferences (throttle for DETECTOR_MAX_FPS).</summary>
    public double InferGapSecs => 1.0 / Math.Max(1, MaxFps);

    private DetectorOptions(string rtspUrl, string modelPath, string eventDir, string camera, string device,
        int inputSize, int frameWidth, double minConf, double burstWindowSecs, double maxFps,
        string natsUrl, string natsSubject, HashSet<int> classes)
    {
        RtspUrl = rtspUrl; ModelPath = modelPath; EventDir = eventDir; Camera = camera;
        Device = device; InputSize = inputSize; FrameWidth = frameWidth; MinConf = minConf;
        BurstWindowSecs = burstWindowSecs; MaxFps = maxFps; NatsUrl = natsUrl;
        NatsSubject = natsSubject; Classes = classes;
    }

    public static DetectorOptions Load()
    {
        string R(string k, string d) => Environment.GetEnvironmentVariable(k) ?? d;
        double RD(string k, double d)
        {
            var v = Environment.GetEnvironmentVariable(k);
            return double.TryParse(v, System.Globalization.CultureInfo.InvariantCulture, out var r) ? r : d;
        }
        int RI(string k, int d)
        {
            var v = Environment.GetEnvironmentVariable(k);
            return int.TryParse(v, out var r) ? r : d;
        }

        return new DetectorOptions(
            R("DETECTOR_RTSP_URL", "rtsp://mediamtx.homelan:8554/entrance_roof_sub"),
            R("DETECTOR_MODEL", "/models/yolo11m.onnx"),
            R("DETECTOR_EVENT_DIR", "/media/events"),
            R("DETECTOR_CAMERA", "entrance_roof"),
            R("DETECTOR_DEVICE", "cuda"),
            RI("DETECTOR_INPUT_SIZE", 640),
            RI("DETECTOR_FRAME_WIDTH", 1280),
            RD("DETECTOR_MIN_CONF", 0.0),
            RD("DETECTOR_BURST_WINDOW_SECS", 2.0),
            RD("DETECTOR_MAX_FPS", 10),
            R("NATS_URL", "nats://nats.homelan:4222"),
            R("NATS_SUBJECT", "surveillance.detector"),
            R("DETECTOR_CLASS", "15").Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries)
                .Select(int.Parse).ToHashSet());
    }
}
