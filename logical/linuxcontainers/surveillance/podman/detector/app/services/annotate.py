#!/usr/bin/env python3
"""Shared box-painting used by the detector's live service (live-push).
Boxes arrive already in
full-frame pixels (predict de-letterboxes), so this module is pure
drawing: cv2.rectangle / putText, nothing else.

draw_boxes() returns a *copy* - the caller's frame stays pristine:
the paint layer draws on the copy, the live pusher still needs the
plain frame underneath.
"""

import numpy as np

import cv2

# a few box colours are enough; cycle by detection index
_PALETTE = [
    (0, 255, 0),  # green
    (0, 128, 255),  # orange
    (255, 128, 0),  # cyan
    (0, 0, 255),  # red
    (255, 0, 255),  # magenta
]


def draw_boxes(frame, boxes, labels, confs, ids=None, thickness=2):
    """Draw (N,4+) xyxy pixel boxes + 'label conf' text onto a copy.

    boxes:  iterable/ndarray of xyxy in full-frame pixels (an (N,5)
            array from a TritonResult works - only the first 4 cols
            are read)
    labels: sequence of label names (len == N)
    confs:  sequence of confidences (len == N)
    ids:    optional sequence of tracker ids aligned to boxes; boxes
            with an id are drawn THICKER and prefixed '#<id>' -
            those are the tracked targets, the rest are one-off dets
    """
    out = frame.copy()
    hgt, wid = out.shape[:2]
    n = len(labels)
    for i in range(n):
        x1, y1, x2, y2 = (
            int(v) for v in (boxes[i][0], boxes[i][1], boxes[i][2], boxes[i][3])
        )
        x1, x2 = max(0, min(x1, wid - 1)), max(0, min(x2, wid - 1))
        y1, y2 = max(0, min(y1, hgt - 1)), max(0, min(y2, hgt - 1))
        if x2 <= x1 or y2 <= y1:
            continue
        is_tracked = ids is not None and i < len(ids) and ids[i] is not None
        color = _PALETTE[i % len(_PALETTE)]
        cv2_thickness = thickness + 1 if is_tracked else thickness
        cv2.rectangle(
            out, (x1, y1), (x2, y2), color, cv2_thickness, lineType=cv2.LINE_AA
        )
        text = (f"#{ids[i]} " if is_tracked else "") + f"{labels[i]} {confs[i]:.2f}"
        cv2.putText(
            out,
            text,
            (x1, max(y1 - 6, 12)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            color,
            cv2_thickness,
            cv2.LINE_AA,
        )
    return out
