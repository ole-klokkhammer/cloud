#!/usr/bin/env python3
"""Lightweight persistent-ID tracker for the detector pipeline.

Session-scoped state owned by the Detector: assigns stable ids to the
tracked labels (person/cat by default) across frames with a greedy IoU
matcher - no dependencies, no numpy, ~60 lines of real logic.

The caller passes ALL of this frame's detections to update(); the
tracker only mints/extends tracks for the configured track_labels and
ignores the rest (those boxes still get drawn by the caller - they just
never get an id).

Contract (all stream-clock time `ts`, seconds since capture session
open):
  * update() is called on EVERY inferred frame - even with zero dets,
    which is exactly how stale tracks get pruned.
  * a track unmatched for > max_age_s is dropped; a missed single
    frame just holds the track's last box (so a 1-frame occlusion
    doesn't kill an id).
  * reset() on stream session restart (the ts domain changed).

DETECTOR_TRACK_LABELS is a list of class *names* - names, not ids,
because ids depend on the model's export but names don't.
"""

from dataclasses import dataclass


def _iou(a, b) -> float:
    """IoU of two xyxy boxes (full-frame pixels)."""
    x1 = max(a[0], b[0])
    y1 = max(a[1], b[1])
    x2 = min(a[2], b[2])
    y2 = min(a[3], b[3])
    inter = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    if inter <= 0:
        return 0.0
    union = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / max(union, 1e-9)


@dataclass
class Track:
    id: int
    label: str
    box: tuple  # xyxy, full-frame pixels (last seen box)
    conf: float
    last_seen: float  # stream ts of the last matched frame
    hits: int = 0


class Tracker:
    """Greedy IoU matching of new detections onto live tracks."""

    def __init__(
        self,
        track_labels=("person", "cat"),
        iou_min: float = 0.25,
        max_age_s: float = 1.0,
        min_conf_new: float = 0.40,
    ):
        self.track_labels = set(track_labels)
        self.iou_min = iou_min
        self.max_age_s = max_age_s
        # a box that is this confident (or better) opens a new track;
        # weaker boxes can only *extend* an existing track. The model's
        # conf is noisy; ids shouldn't be minted on near-threshold dets.
        self.min_conf_new = min_conf_new
        self.tracks: list[Track] = []
        self._next_id = 1

    @property
    def count(self) -> int:
        """Number of live tracks (for log/event bookkeeping)."""
        return len(self.tracks)

    def reset(self):
        """Stream session restarted: the ts domain changed - drop all
        state (ids restart, no cross-session tracking is wanted)."""
        self.tracks = []
        self._next_id = 1

    def update(self, dets, ts: float) -> tuple:
        """Match this frame's dets onto live tracks.

        dets: a list of (conf, label, box) - box = xyxy full-frame
        pixels. May be empty. The tracker only mints/extends tracks for
        the configured track_labels; every element of `dets` is
        accounted for in the returned alignment.

        Returns (ids_aligned, had_active):
          ids_aligned: list aligned to `dets` (same length) - the
            track id for dets[i] when it is a tracked target that
            matched or was minted this frame, else None (an untracked
            label, or a tracked det too weak to mint AND unmatched,
            gets None). The caller feeds it straight to draw_boxes().
          had_active: True when any tracked target matched/was minted
            this frame - the live pusher uses it to prefer fresh
            frames over the frozen still.

        A track keeps the label it was minted with - so a 1-frame
        person<->cat model glitch can't repaint an id.
        """
        # prune dead tracks first
        self.tracks = [t for t in self.tracks if ts - t.last_seen <= self.max_age_s]

        ids_aligned = [None] * len(dets)

        # only the configured tracked labels can claim or mint a track
        cands = [
            (di, conf, label, box)
            for di, (conf, label, box) in enumerate(dets)
            if label in self.track_labels
        ]

        # greedy match: best IoU pair first, higher conf wins ties, and a
        # candidate may only claim a track of its own label
        pairs = []
        for ti, t in enumerate(self.tracks):
            for di, conf, label, box in cands:
                if label != t.label:
                    continue
                score = _iou(t.box, box)
                if score >= self.iou_min:
                    pairs.append((score, conf, ti, di))
        pairs.sort(key=lambda p: (p[0], p[1]), reverse=True)

        used_t, used_c = set(), set()
        had_active = False
        for _score, _conf, ti, di in pairs:
            if ti in used_t or di in used_c:
                continue
            used_t.add(ti)
            used_c.add(di)
            conf, _label, box = dets[di]
            t = self.tracks[ti]
            t.box, t.conf, t.last_seen = box, conf, ts
            t.hits += 1
            ids_aligned[di] = t.id
            had_active = True

        # confident tracked dets nobody claimed open their own track
        for di, conf, _label, box in cands:
            if di in used_c or conf < self.min_conf_new:
                continue
            t = Track(self._next_id, _label, tuple(box), conf, ts, hits=1)
            self._next_id += 1
            self.tracks.append(t)
            ids_aligned[di] = t.id
            had_active = True

        return ids_aligned, had_active
