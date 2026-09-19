// RTSP capture: ffprobe the stream once for its resolution, then ffmpeg raw BGR24 pipe.
using System.Diagnostics;

namespace Detector;

internal static class Capture
{
    /// <summary>ffprobe the stream once for its native resolution.</summary>
    public static (int W, int H) ProbeResolution(string url)
    {
        var psi = new ProcessStartInfo("ffprobe", new[]
            { "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", url })
        { RedirectStandardOutput = true, RedirectStandardError = true, UseShellExecute = false };
        using var p = Process.Start(psi)!;
        string outp = p.StandardOutput.ReadToEnd();
        p.StandardError.ReadToEnd();
        p.WaitForExit();
        var parts = outp.Split(',', StringSplitOptions.TrimEntries | StringSplitOptions.RemoveEmptyEntries);
        if (parts.Length < 2 || !int.TryParse(parts[0], out var w) || !int.TryParse(parts[1], out var h))
            throw new InvalidOperationException($"ffprobe failed for {url}: '{outp.Trim()}'");
        return (w, h);
    }

    /// <summary>ffmpeg RTSP -> raw BGR24 frames on stdout at the exact target size.</summary>
    public static Process StartFfmpeg(string url, int w, int h)
    {
        var psi = new ProcessStartInfo("ffmpeg", new[]
        {
            "-nostdin", "-loglevel", "error", "-rtsp_transport", "tcp", "-i", url,
            "-an", "-vf", $"scale={w}:{h}", "-f", "rawvideo", "-pix_fmt", "bgr24", "pipe:1",
        })
        { UseShellExecute = false, RedirectStandardOutput = true, RedirectStandardError = true };
        var p = Process.Start(psi)!;
        // drain stderr so the pipe never fills
        _ = p.StandardError.ReadToEndAsync();
        return p;
    }
}
