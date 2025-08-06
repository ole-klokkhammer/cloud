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
        string outputFile = $"{outputDir}/index.m3u8";

        string segmentDir = $"{outputDir}/segments";
        if (!Directory.Exists(segmentDir))
        {
            Directory.CreateDirectory(segmentDir);
        }
        string segmentPattern = $"{segmentDir}/segment%03d.ts";
        logger.LogDebug($"Segment files will be: {segmentPattern}");

        string ffmpegArgs = string.Join(" ", new[]
        {
            "-rtsp_transport tcp",
            $"-i {rtspUrl}",
            "-c:v h264",
            "-c:a aac",
            "-f hls",
            "-hls_time 4",
            "-hls_list_size 151200",
            "-hls_flags delete_segments+append_list",
            $"-hls_segment_filename {segmentPattern}",
            outputFile
        });
        ffmpegProcess = Process.Start(new ProcessStartInfo
        {
            FileName = "/usr/bin/ffmpeg",
            Arguments = ffmpegArgs,
            RedirectStandardError = true,
            RedirectStandardOutput = true,
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
    }
}