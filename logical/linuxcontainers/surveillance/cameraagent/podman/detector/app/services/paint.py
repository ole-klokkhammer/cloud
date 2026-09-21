#!/usr/bin/env python3
"""Paint triton-detected boxes onto one still.

Debug/trust harness: proves what yolo26x actually returns for a real
frame, through the SAME TritonClient + env config the detector uses.
It is NOT part of the hot path - run it by hand:

    # grab one live frame from the RTSP, paint it, save annotated JPEG:
    python -m paint

    # or load a specific still instead of the live stream:
    python -m paint /detector/probe.jpg

    # where to write the annotated result (default: next to the
    # input; a live frame goes to $DETECTOR_EVENT_DIR):
    python -m paint --out /detector/paint_out.jpg

Usage:
    python -m paint [INPUT_IMAGE] [--live] [--out PATH]

Output:
    the annotated frame is written (JPEG, BGR, boxes drawn in pixels
    full-frame coords, "label conf" text above each box). It ALSO
    prints, per detection, the label + conf + pixel xyxy - so even
    without opening the image you can eyeball whether the boxes land
    on the right pixels of the right objects.
"""

import argparse
import logging
import sys

import cv2
import numpy as np

from config import environment
from services.triton_client import COCO_NAMES, TritonClient

logger = logging.getLogger("paint")

# a few box colours are enough; cycle by label
_PALETTE = [
    (0, 255, 0),  # green
    (0, 128, 255),  # orange
    (255, 128, 0),  # cyan
    (0, 0, 255),  # red
    (255, 0, 255),  # magenta
]


def _grab_live_frame() -> np.ndarray:
    """One BGR frame from the RTSP (best effort: a couple of warm-up
    reads so ffmpeg's buffers fill). Raises if the stream can't open."""
    cap = cv2.VideoCapture(environment.rtsp_url)
    try:
        ok, frame = cap.read()
        for _ in range(3):  # warm up - early frames from RTSP are often black
            ok, frame = cap.read()
        if not ok or frame is None:
            raise RuntimeError(f"could not grab frame from {environment.rtsp_url}")
        return frame
    finally:
        cap.release()


def _load_image(path: str) -> np.ndarray:
    img = cv2.imread(path)
    if img is None:
        raise SystemExit(f"[paint] could not read image {path!r}")
    return img


def _draw(
    frame: np.ndarray,
    boxes: np.ndarray,
    labels: list,
    confs: np.ndarray,
) -> np.ndarray:
    """Draw (N,5) xyxy pixel boxes + labels onto a BGR frame copy.

    boxes come already in full-frame pixels (predict de-letterboxed
    them), so no coordinate math here - just cv2.rectangle/putText."""
    out = frame.copy()
    hgt, wid = out.shape[:2]
    for i in range(len(labels)):
        x1, y1, x2, y2, conf = (int(v) for v in (*np.floor(boxes[i, :4]), boxes[i, 4]))
        x1 = max(0, min(x1, wid - 1))
        y1 = max(0, min(y1, hgt - 1))
        x2 = max(0, min(x2, wid - 1))
        y2 = max(0, min(y2, hgt - 1))
        if x2 <= x1 or y2 <= y1:
            continue
        color = _PALETTE[i % len(_PALETTE)]
        cv2.rectangle(out, (x1, y1), (x2, y2), color, 2)
        text = f"{labels[i]} {confs[i]:.2f}"
        cv2.putText(
            out,
            text,
            (x1, max(y1 - 6, 12)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            color,
            2,
            cv2.LINE_AA,
        )
    return out


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)-7s %(message)s")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("image", nargs="?", default=None, help="input still (BGR path)")
    ap.add_argument(
        "--live",
        action="store_true",
        help="grab a live RTSP frame instead of an input file",
    )
    ap.add_argument("--out", default=None, help="output path (default: auto)")
    ap.add_argument(
        "--no-filter",
        action="store_true",
        help="ignore the DETECTOR_CLASS env filter; show ALL detections",
    )
    args = ap.parse_args()

    frame = (
        _grab_live_frame()
        if (args.live or args.image is None)
        else _load_image(args.image)
    )
    src = environment.rtsp_url if args.live else (args.image or "live")

    client = TritonClient(
        environment.triton_url,
        environment.triton_model,
        imgsz=environment.triton_input_size,
        names=environment.triton_class_labels or COCO_NAMES,
    )
    logger.info(
        f"painting {src}: triton={environment.triton_url} "
        f"model={environment.triton_model} conf>={environment.triton_min_conf} "
        f"iou={environment.triton_iou}"
    )
    client.load(
        conf=environment.triton_min_conf,
        iou=environment.triton_iou,
        classes=None if args.no_filter else environment.triton_class_filter,
    )
    res = client.predict(
        frame,
        conf=environment.triton_min_conf,
        iou=environment.triton_iou,
        classes=None if args.no_filter else environment.triton_class_filter,
    )

    # print the raw answer - the trust check is mostly reading THIS
    if res.count == 0:
        print(
            f"[paint] 0 detections (conf>={environment.triton_min_conf}, "
            f"class_filter={'all' if args.no_filter else environment.class_filter_str})"
        )
    else:
        confs = res.boxes[:, 4]
        for i, (lab, box) in enumerate(zip(res.labels, res.boxes)):
            x1, y1, x2, y2, c = box
            print(
                f"[paint] #{i:02d} {lab:<6} conf={c:.3f} "
                f"xyxy=[{x1:.0f},{y1:.0f},{x2:.0f},{y2:.0f}]"
            )

    painted = _draw(frame, res.boxes, res.labels, res.boxes[:, 4])
    out = args.out
    if out is None:
        out = (
            "paint_out.jpg"
            if args.live or args.image is None
            else args.image + ".out.jpg"
        )
        # default drop goes to the /detector media mount so it is visible on the LXC
        if not out.startswith("/"):
            out = f"{environment.event_dir.rstrip('/')}/{out}"
    ok = cv2.imwrite(out, painted)
    print(f"[paint] wrote {out if ok else 'FAILED'} ({res.count} boxes)")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
