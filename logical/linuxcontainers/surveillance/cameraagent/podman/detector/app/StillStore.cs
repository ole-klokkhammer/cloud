// JPEG stills to /detector/events - the embedder polls this dir (names: cat_YYYYMMDD_HHMMSS.jpg).
using SixLabors.ImageSharp;
using SixLabors.ImageSharp.Formats.Jpeg;
using SixLabors.ImageSharp.PixelFormats;

namespace Detector;

internal static class StillStore
{
    /// <summary>Save a BGR24 frame as a JPEG (embedder's STILL_RE naming: cat_YYYYMMDD_HHMMSS.jpg).</summary>
    public static string Save(byte[] bgr, int fw, int fh, DateTime ts, string eventDir)
    {
        string file = Path.Combine(eventDir, $"cat_{ts:yyyyMMdd_HHmmss}.jpg");
        using var img = Image.LoadPixelData<Bgr24>(bgr, fw, fh);
        img.SaveAsJpeg(file, new JpegEncoder { Quality = 85 });
        return file;
    }
}
