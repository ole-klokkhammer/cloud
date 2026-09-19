// ONNX inference: session build (CUDA EP), letterbox/resize preprocessing, output decode.
using Microsoft.ML.OnnxRuntime;

namespace Detector;

/// <summary>One NMS'd detection, in ONNX-input (letterbox) pixel space.</summary>
internal sealed class Detection
{
    public double X1, Y1, X2, Y2;
    public double Conf;
    public int ClassId;
}

internal sealed class YoloModel : IDisposable
{
    private readonly InferenceSession _session;
    public string InputName { get; }
    public int InputSize { get; }

    public YoloModel(string modelPath, string device, int inputSize)
    {
        InputSize = inputSize;
        var options = new SessionOptions();
        if (device == "cuda")
        {
            try
            {
                options.AppendExecutionProvider_CUDA(0);
                Log.Info("device: cuda (onnx runtime CUDA execution provider)");
            }
            catch (Exception e)
            {
                // CUDA EP fails to load when the container can't see the CUDA 13.x runtime
                // libs (libcublas/libcudnn via the /opt/cuda-runtime mount + LD_LIBRARY_PATH).
                // Fall back to CPU instead of crash-looping: stills keep flowing, just slower.
                Log.Info($"cuda execution provider unavailable ({e.Message}) - running on CPU; " +
                         "check the CUDA runtime mount/LD_LIBRARY_PATH and restart for GPU");
            }
            // TensorRT is faster still, one line away (pick an ORT release whose bundled
            // TRT supports sm_120 = consumer Blackwell, TRT 10.3-generation):
            // options.AppendExecutionProvider_Tensorrt(new OrtTensorRTProviderOptions {
            //     TrtMaxWorkspaceSize = 1 << 30, TrtPooledTemporaryMemory = true, TrtForcePending = false });
        }
        else
        {
            Log.Info("device: cpu (DETECTOR_DEVICE=cpu) - no GPU, slow");
        }

        _session = new InferenceSession(modelPath, options);
        InputName = _session.InputMetadata.Keys.First();
        Log.Info($"model ready: {modelPath} (input '{InputName}', {inputSize}x{inputSize})");
    }

    /// <summary>
    /// BGR24 [h,w,3] -> NCHW float32 [3, InputSize, InputSize]: bilinear downscale,
    /// letterbox (padded with ultralytics' 114 grey), normalize (x/255-0.5)/0.5.
    /// Outputs the mapping so boxes can be un-mapped back to frame pixels.
    /// </summary>
    public void PrepareInput(byte[] bgr, int fw, int fh, float[] input,
        out double scale, out double ox, out double oy)
    {
        scale = Math.Min((double)InputSize / fw, (double)InputSize / fh);
        int nw = (int)Math.Round(fw * scale);
        int nh = (int)Math.Round(fh * scale);
        ox = (InputSize - nw) / 2.0;
        oy = (InputSize - nh) / 2.0;

        const float pad = -0.117647f; // (114/255 - 0.5) / 0.5 == ultralytics letterbox grey
        Array.Fill(input, pad);

        for (int y = 0; y < InputSize; y++)
        {
            double sy = (y - oy + 0.5) / scale - 0.5;
            int y0 = Clamp((int)Math.Floor(sy), 0, fh - 1);
            int y1 = Clamp((int)Math.Ceiling(sy), 0, fh - 1);
            double wy = y0 == y1 ? 0 : sy - y0;
            for (int x = 0; x < InputSize; x++)
            {
                double sx = (x - ox + 0.5) / scale - 0.5;
                int x0 = Clamp((int)Math.Floor(sx), 0, fw - 1);
                int x1 = Clamp((int)Math.Ceiling(sx), 0, fw - 1);
                double wx = x0 == x1 ? 0 : sx - x0;
                int p = (y * InputSize + x) * 3;
                for (int c = 0; c < 3; c++)
                {
                    int i00 = (y0 * fw + x0) * 3 + c;
                    int i01 = (y0 * fw + x1) * 3 + c;
                    int i10 = (y1 * fw + x0) * 3 + c;
                    int i11 = (y1 * fw + x1) * 3 + c;
                    double v = (1 - wx) * ((1 - wy) * bgr[i00] + wy * bgr[i10])
                             + wx * ((1 - wy) * bgr[i01] + wy * bgr[i11]);
                    input[p] = (float)((v / 255.0 - 0.5) / 0.5);
                }
            }
        }
    }

    /// <summary>
    /// Run inference. Expects an nms=True export: [1, N, 6] = x1 y1 x2 y2 score class,
    /// in input (letterbox) pixels, best-first, N = max_det (300) with zero-score padding.
    /// </summary>
    public List<Detection> Infer(float[] input, HashSet<int> classes, double minConf)
    {
        var inputVal = OrtValue.CreateTensorValueFromMemory(input, new long[] { 1, 3, InputSize, InputSize });
        using var results = _session.Run(new RunOptions(), new[] { InputName }, new[] { inputVal }, Array.Empty<string>());
        var t = results.First();
        var shape = t.GetTensorTypeAndShape().Shape;
        if (shape.Length != 3 || shape[2] != 6)
            throw new InvalidOperationException(
                $"unexpected ONNX output shape [{string.Join(",", shape)}] - export with " +
                "'yolo export ... format=onnx nms=True conf=... iou=...' (see README)");

        var data = t.GetTensorDataAsSpan<float>();
        var dets = new List<Detection>();
        int n = (int)shape[1];
        for (int i = 0; i < n; i++)
        {
            double conf = data[i * 6 + 4];
            if (conf <= 0.0 || conf < minConf) continue;  // 0-score rows are NMS padding
            int cls = (int)Math.Round(data[i * 6 + 5]);
            if (!classes.Contains(cls)) continue;
            dets.Add(new Detection
            {
                X1 = data[i * 6 + 0],
                Y1 = data[i * 6 + 1],
                X2 = data[i * 6 + 2],
                Y2 = data[i * 6 + 3],
                Conf = conf,
                ClassId = cls,
            });
        }
        dets.Sort((a, b) => b.Conf.CompareTo(a.Conf)); // best-first (graph sorts too; be defensive)
        return dets;
    }

    /// <summary>Letterbox/un-scale: ONNX-input pixel -> original-frame pixel.</summary>
    public static double Unmap(double v, double scale, double off) => (v - off) / scale;

    private static int Clamp(int v, int lo, int hi) => v < lo ? lo : v > hi ? hi : v;

    public void Dispose() => _session.Dispose();
}
