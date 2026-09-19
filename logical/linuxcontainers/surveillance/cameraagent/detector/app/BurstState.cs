// Best-frame selection: keep a bounded ring of detection frames per burst,
// score = confidence * target-area-fraction ("clearest/closest" wins).
using System.Collections.Generic;

namespace Detector;

/// <summary>A candidate frame for storage: one inferred frame of a burst.</summary>
internal sealed class Candidate
{
    public double Score;      // conf * areaFraction - "clearest/closest" wins
    public double Conf;
    public DateTime Ts;
    public byte[] Bgr = null!; // BGR24 frame (original resolution)
    public Detection Det = null!;
}

/// <summary>The winner of a closed burst, plus how many frames produced it.</summary>
internal sealed record ClosedBurst(Candidate Best, int Frames);

internal sealed class BurstState
{
    private const int RingMax = 16;              // bound memory on long bursts
    private readonly Queue<Candidate> _ring = new();
    private Candidate? _best;
    private double _lastDetAt = -1;
    public int BurstFrames { get; private set; }

    /// <summary>Record a detection frame; it becomes the burst's best if it scores highest.</summary>
    public void OnDetected(double now, Candidate cand)
    {
        _lastDetAt = now;
        BurstFrames++;
        _ring.Enqueue(cand);
        if (_ring.Count > RingMax) _ring.Dequeue();
        if (_best is null || cand.Score > _best.Score) _best = cand;
    }

    /// <summary>Return the burst winner if the burst has closed (no detection for windowSecs), else null.</summary>
    public ClosedBurst? TryClose(double now, double windowSecs)
    {
        if (_best is null || now - _lastDetAt < windowSecs) return null;
        var burst = new ClosedBurst(_best, BurstFrames);
        _best = null;
        _ring.Clear();
        BurstFrames = 0;
        return burst;
    }
}
