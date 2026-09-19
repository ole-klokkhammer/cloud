// detector (.NET): GPU YOLO object detection for the camagent LXC.
//
// pipeline:  mediamtx RTSP substream --ffmpeg--> BGR24 frames
//            --> bilinear downscale + letterbox (to the ONNX input size)
//            --> ONNX Runtime (CUDA execution provider, sm_120)
//            --> per-burst BEST-FRAME selection (conf x area score)
//            --> stills on /detector/events + one NATS event per burst
//
// this file: config wiring + main loop. domain pieces live in their own files:
//   Config.cs, Capture.cs, YoloModel.cs, BurstState.cs, StillStore.cs, NatsBus.cs,
//   Log.cs, Labels.cs. model is an exported ONNX artifact (see README).
using System.Diagnostics;
using System.Runtime.InteropServices;

namespace Detector;

internal static class Program
{
    private static volatile bool _stop;

    private static async Task Main()
    {
        var cfg = DetectorOptions.Load();
        Directory.CreateDirectory(cfg.EventDir);
        Log.Info($"watching {cfg.RtspUrl} (classes: {string.Join(",", cfg.Classes)})");

        // ONNX session (GPU) - owns model + input metadata
        var model = new YoloModel(cfg.ModelPath, cfg.Device, cfg.InputSize);

        // probe stream resolution once (ffprobe)
        var (srcW, srcH) = Capture.ProbeResolution(cfg.RtspUrl);
        int frameH = (int)(2 * Math.Round((double)srcH * cfg.FrameWidth / srcW / 2)); // even
        Log.Info($"stream {srcW}x{srcH} -> decode {cfg.FrameWidth}x{frameH} (stills at this res)");

        // NATS (initial; events skipped while it's down, stills unaffected)
        var bus = new NatsBus(cfg.NatsUrl, cfg.NatsSubject);
        await bus.ConnectAsync();

        // per-stream scratch
        byte[] frame = new byte[cfg.FrameWidth * frameH * 3];
        float[] input = new float[3 * cfg.InputSize * cfg.InputSize];
        double inferScale = 0, inferOx = 0, inferOy = 0;
        var state = new BurstState();
        var sw = Stopwatch.StartNew();
        long frames = 0; double lastHeart = 0;
        double lastInferAt = 0;
        Process? ffmpeg = null;

        using var sigterm = PosixSignalRegistration.Create(PosixSignal.SIGTERM, _ => _stop = true);
        Console.CancelKeyPress += (_, e) => { e.Cancel = true; _stop = true; };

        while (!_stop)
        {
            if (ffmpeg is null || ffmpeg.HasExited)
            {
                ffmpeg = Capture.StartFfmpeg(cfg.RtspUrl, cfg.FrameWidth, frameH);
                Log.Info($"ffmpeg decode started ({cfg.FrameWidth}x{frameH} bgr24 raw pipe)");
            }

            try
            {
                // rawvideo frames are exact-size; pipes may deliver them in 64KB chunks,
                // so ReadExactly (loops until the whole frame is in, throws at true EOF)
                ffmpeg.StandardOutput.BaseStream.ReadExactly(frame);
            }
            catch (Exception e)
            {
                Log.Info($"stream lost ({e.Message}); restarting in 5s");
                ffmpeg.Dispose();
                ffmpeg = null;
                Thread.Sleep(5000);
                lastInferAt = 0;
                continue;
            }
            frames++;
            double now = sw.Elapsed.TotalSeconds;
            if (now - lastInferAt < cfg.InferGapSecs)
                continue;                        // throttle to DETECTOR_MAX_FPS
            lastInferAt = now;

            model.PrepareInput(frame, cfg.FrameWidth, frameH, input, out inferScale, out inferOx, out inferOy);
            var dets = model.Infer(input, cfg.Classes, cfg.MinConf);
            DateTime ts = DateTime.Now;

            if (dets.Count > 0)
            {
                var top = dets[0];              // NMS export: sorted best-first
                double areaFrac = ((top.X2 - top.X1) * (top.Y2 - top.Y1)) / ((double)cfg.InputSize * cfg.InputSize);
                state.OnDetected(now, new Candidate
                {
                    Score = top.Conf * areaFrac,
                    Conf = top.Conf,
                    Ts = ts,
                    Bgr = (byte[])frame.Clone(), // ring keeps its own copy
                    Det = top,
                });

                Log.Json(new
                {
                    @event = "detection",
                    camera = cfg.Camera,
                    ts = ts.ToString("o"),
                    dets = dets.Count,
                    best_conf = Math.Round(top.Conf, 3),
                    bbox = new[] {
                        (int)YoloModel.Unmap(top.X1, inferScale, inferOx),
                        (int)YoloModel.Unmap(top.Y1, inferScale, inferOy),
                        (int)YoloModel.Unmap(top.X2, inferScale, inferOx),
                        (int)YoloModel.Unmap(top.Y2, inferScale, inferOy) },
                });
            }
            else if (state.TryClose(now, cfg.BurstWindowSecs) is { } burst)
            {
                // burst closed: store the BEST frame, emit one event
                string file = StillStore.Save(burst.Best.Bgr, cfg.FrameWidth, frameH, burst.Best.Ts, cfg.EventDir);
                Log.Info($"best still stored: {file} (burst of {burst.Frames} detection frames, " +
                          $"best conf {burst.Best.Conf:F2})");
                await bus.PublishBurstAsync(cfg.Camera, file, burst.Best, burst.Frames,
                    inferScale, inferOx, inferOy);
            }

            if (now - lastHeart >= 60)
            {
                lastHeart = now;
                Log.Json(new
                {
                    @event = "heartbeat",
                    frames,
                    fps = Math.Round(frames / Math.Max(1, now), 2),
                    last_dets = dets.Count,
                    stream_ok = ffmpeg != null,
                });
            }
        }

        Log.Info("stopping");
        ffmpeg?.Kill();
        await bus.DisposeAsync();
        model.Dispose();
    }
}
