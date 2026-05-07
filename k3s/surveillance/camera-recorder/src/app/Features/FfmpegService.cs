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
        string outputDir = AppEnvironment.OutputDirectory;
        if (!Directory.Exists(outputDir)) Directory.CreateDirectory(outputDir);

        var psi = new ProcessStartInfo
        {
            FileName = "/usr/bin/ffmpeg",
            RedirectStandardError = true,
            UseShellExecute = false,
            CreateNoWindow = true
        };

        // Global options
        psi.ArgumentList.Add("-hide_banner");
        psi.ArgumentList.Add("-y");
        psi.ArgumentList.Add("-loglevel");
        psi.ArgumentList.Add("error");

        // Input
        psi.ArgumentList.Add("-rtsp_transport");
        psi.ArgumentList.Add("tcp");
        psi.ArgumentList.Add("-i");
        psi.ArgumentList.Add(rtspUrl);

        // video  
        psi.ArgumentList.Add("-c:v");
        psi.ArgumentList.Add("copy");

        // Audio
        psi.ArgumentList.Add("-c:a");
        psi.ArgumentList.Add("copy");

        // metadata
        var utcNow = DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ"); // RFC3339 UTC
        psi.ArgumentList.Add("-metadata"); psi.ArgumentList.Add($"creation_time={utcNow}");
        psi.ArgumentList.Add("-metadata"); psi.ArgumentList.Add($"date={utcNow}");        // extra tag some players use
        psi.ArgumentList.Add("-metadata"); psi.ArgumentList.Add("title=Entrance Roof");   // optional

        // flags
        psi.ArgumentList.Add("-flags");
        psi.ArgumentList.Add("+global_header");

        // handle broken timestamps from some cameras 
        psi.ArgumentList.Add("-use_wallclock_as_timestamps");
        psi.ArgumentList.Add("1");
        psi.ArgumentList.Add("-reset_timestamps");
        psi.ArgumentList.Add("1");
        psi.ArgumentList.Add("-segment_atclocktime");
        psi.ArgumentList.Add("1");

        // allow strftime-style filenames (e.g. %Y%m%dT%H%M%S)
        psi.ArgumentList.Add("-strftime");
        psi.ArgumentList.Add("1");

        // Segment muxer
        psi.ArgumentList.Add("-f");
        psi.ArgumentList.Add("segment");
        psi.ArgumentList.Add("-segment_time");
        psi.ArgumentList.Add("900");
        psi.ArgumentList.Add("-segment_format");
        psi.ArgumentList.Add("mkv");

        // Output pattern
        psi.ArgumentList.Add(Path.Combine(outputDir, "%Y%m%dT%H%M%S.mkv"));

        ffmpegProcess = Process.Start(psi) ?? throw new InvalidOperationException("Failed to start FFmpeg process.");

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