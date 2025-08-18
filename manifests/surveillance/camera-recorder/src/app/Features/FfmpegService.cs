using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using System.Diagnostics;

public class FfmpegService : BackgroundService
{
    private readonly ILogger<FfmpegService> logger;
    private Process? ffmpegProcess;

    public FfmpegService(ILogger<FfmpegService> logger)
    {
        this.logger = logger;
    }

    protected override async Task ExecuteAsync(CancellationToken token)
    {
        logger.LogInformation("Starting FFmpeg process...");

        string rtspUrl = AppEnvironment.RtspUrl;
        logger.LogDebug($"Using RTSP URL: {rtspUrl}");
        string outputDir = AppEnvironment.OutputDirectory;
        logger.LogDebug($"Using output directory: {outputDir}");
        if (!Directory.Exists(outputDir))
        {
            Directory.CreateDirectory(outputDir);
        }
        string pattern = Path.Combine(outputDir, "%Y%m%dT%H%M%S.mkv");

        string ffmpegArgs = string.Join(" ", new[]
        {
            "-hide_banner -y",
            "-loglevel error",

            // Input
            "-rtsp_transport tcp",
            "-use_wallclock_as_timestamps 1",
            $"-i {rtspUrl}",

            // Copy codecs
            "-c:v copy",
            "-c:a copy",
            "-flags +global_header",

            // Segment muxer options
            "-f segment",
            "-reset_timestamps 1",
            "-strftime 1",
            "-segment_time 900",
            "-segment_atclocktime 1",
            "-segment_format mkv",

            // **Final: a single filename pattern with strftime**
            $"\"{pattern}\""
        });

        ffmpegProcess = Process.Start(new ProcessStartInfo
        {
            FileName = "/usr/bin/ffmpeg",
            Arguments = ffmpegArgs,
            RedirectStandardError = true,
            UseShellExecute = false,
            CreateNoWindow = true
        });
        if (ffmpegProcess == null)
        {
            throw new InvalidOperationException("Failed to start FFmpeg process.");
        }

        logger.LogInformation("FFmpeg process started with PID {Pid}", ffmpegProcess.Id);
        while (!ffmpegProcess.HasExited && !token.IsCancellationRequested)
        {
            string? line = await ffmpegProcess.StandardError.ReadLineAsync();
            if (line != null)
            {
                logger.LogDebug("[FFmpeg] {Line}", line);
            }

            await Task.Delay(10, token);
        }

        logger.LogInformation("Stopping FFmpeg process...");
        if (ffmpegProcess != null && !ffmpegProcess.HasExited)
        {
            ffmpegProcess.Kill();
            await ffmpegProcess.WaitForExitAsync(token);
        }
        logger.LogInformation("FFmpeg process has exited.");

        // ensure pod is restarted if FFmpeg stops unexpectedly
        throw new OperationCanceledException("FFmpeg service has been stopped.");
    }
}