"""Triton gRPC client for the detector service.

The model (.onnx, in the LXC's /models) is served by the triton container
(surveillance/triton image, onnxruntime backend) - not by this process.
This client does what ultralytics used to do in-process, around the
remote inference:
  * letterbox the frame (center pad 114, scaleup - exactly the
    predictor's convention) into the model's 640x640 input
  * ship it as an FP32 NCHW tensor over gRPC (triton port 8001)
  * post-process the raw model output: conf filter, NMS, class filter,
    de-letterbox back to full-frame pixels, class ids -> names.

The client and the server share no config besides the server URL +
model name. The model supports two export layouts, auto-detected from
the output shape at load() time:
  raw     out [84, 8400]   4 box (cxywh in 640-space) + 80 sigmoid
                            class scores -> this client runs the NMS
  end2end out [300, 6]     x1,y1,x2,y2,conf,cls, NMS already in the
                            graph -> this client only filters
"""

import logging
import time
from typing import List, Optional, Sequence

import cv2
import numpy as np
import tritonclient.grpc as tc_grpc

logger = logging.getLogger("detector")

# the model was exported at this size; DETECTOR_INPUT_SIZE must match
_LETTERBOX_PAD = 114
_TENSOR_DTYPE = np.float32

# the triton gRPC channel limits - the tensors are ~5MB, keep headroom
_CHANNEL_OPTIONS = [
    ("grpc.max_send_message_length", 64 * 1024 * 1024),
    ("grpc.max_receive_message_length", 64 * 1024 * 1024),
]

# triton startup (model load + server warmup) takes ~30-60s; the client
# retries for this long, then init fails (systemd retries the service)
_READY_TIMEOUT_S = 120.0

# stock .pt/.onnx = COCO; a fine-tuned model overrides via
# DETECTOR_CLASS_NAMES (see config.py)
COCO_NAMES = (
    "person",
    "bicycle",
    "car",
    "motorcycle",
    "airplane",
    "bus",
    "train",
    "truck",
    "boat",
    "traffic light",
    "fire hydrant",
    "stop sign",
    "parking meter",
    "bench",
    "bird",
    "cat",
    "dog",
    "horse",
    "sheep",
    "cow",
    "elephant",
    "bear",
    "zebra",
    "giraffe",
    "backpack",
    "umbrella",
    "handbag",
    "tie",
    "suitcase",
    "frisbee",
    "skis",
    "snowboard",
    "sports ball",
    "kite",
    "baseball bat",
    "baseball glove",
    "skateboard",
    "surfboard",
    "tennis racket",
    "bottle",
    "wine glass",
    "cup",
    "fork",
    "knife",
    "spoon",
    "bowl",
    "banana",
    "apple",
    "sandwich",
    "orange",
    "broccoli",
    "carrot",
    "hot dog",
    "pizza",
    "donut",
    "cake",
    "chair",
    "couch",
    "potted plant",
    "bed",
    "dining table",
    "toilet",
    "tv",
    "laptop",
    "mouse",
    "remote",
    "keyboard",
    "cell phone",
    "microwave",
    "oven",
    "toaster",
    "sink",
    "refrigerator",
    "book",
    "clock",
    "vase",
    "scissors",
    "teddy bear",
    "hair drier",
    "toothbrush",
)


def _letterbox(frame: np.ndarray, size: int):
    """frame (H,W,3) BGR -> (tensor [1,3,size,size] FP32 RGB/255, meta).

    Mirrors ultralytics' predict letterbox exactly (auto=False,
    scaleup, center=True, pad 114, INTER_LINEAR): the de-letterbox math
    below must match what the model saw, or boxes drift."""
    h, w = frame.shape[:2]
    r = min(size / h, size / w)  # scaleup allowed, like the predictor
    nw, nh = round(w * r), round(h * r)
    dw, dh = size - nw, size - nh
    # the -0.1/+0.1 nudge keeps top+bottom == dh exactly (ultralytics'
    # round-half-down trick)
    top, left = round(dh / 2 - 0.1), round(dw / 2 - 0.1)
    resized = cv2.resize(frame, (nw, nh), interpolation=cv2.INTER_LINEAR)
    canvas = np.full((size, size, 3), _LETTERBOX_PAD, dtype=np.uint8)
    canvas[top : top + nh, left : left + nw] = resized
    rgb = canvas[:, :, ::-1].astype(_TENSOR_DTYPE) / 255.0
    tensor = np.ascontiguousarray(rgb.transpose(2, 0, 1))[None]
    meta = {"r": r, "top": top, "left": left}
    return tensor, meta


def _nms(cxywh: np.ndarray, confs: np.ndarray, iou_th: float) -> np.ndarray:
    """Greedy NMS on (K,4) cxywh boxes + (K,) scores; returns kept
    indices, highest-score-first. Vectorized; K is post-conf-filter
    (small in practice, 8400 at worst)."""
    if cxywh.shape[0] == 0:
        return np.zeros(0, dtype=np.int64)
    x1 = cxywh[:, 0] - cxywh[:, 2] / 2
    y1 = cxywh[:, 1] - cxywh[:, 3] / 2
    x2 = cxywh[:, 0] + cxywh[:, 2] / 2
    y2 = cxywh[:, 1] + cxywh[:, 3] / 2
    area = np.maximum(x2 - x1, 0.0) * np.maximum(y2 - y1, 0.0)
    keep = []
    rest = confs.argsort()[::-1]
    while rest.size:
        i = int(rest[0])
        keep.append(i)
        if rest.size == 1:
            break
        inter = (
            np.maximum(0.0, np.minimum(x2[i], x2[rest[1:]]) - np.maximum(x1[i], x1[rest[1:]]))
            * np.maximum(0.0, np.minimum(y2[i], y2[rest[1:]]) - np.maximum(y1[i], y1[rest[1:]]))
        )
        iou = inter / (area[i] + area[rest[1:]] - inter + 1e-9)
        rest = rest[1:][iou <= iou_th]
    return np.asarray(keep, dtype=np.int64)


class TritonResult:
    """One frame's detections, as the detector will use them: conf- and
    class-filtered, NMS'd; boxes in full-frame pixels."""

    __slots__ = ("boxes", "labels")

    def __init__(self, boxes: np.ndarray, labels: List[str]):
        self.boxes = boxes  # (N, 5) float32: x1, y1, x2, y2, conf
        self.labels = labels

    @property
    def count(self) -> int:
        return len(self.labels)


class TritonClient:
    """The triton-side counterpart of the old in-process YOLO object:
    .load() (server readiness wait + one sanity inference), .predict(
    frame, ...) -> TritonResult. Hot-path contract: exceptions
    propagate (the caller backs off); per-frame state is the gRPC
    channel + the auto-detected output layout only.
    """

    def __init__(
        self,
        server_url: str,
        model: str = "detector",
        imgsz: int = 640,
        timeout: float = 15.0,
        names: Optional[Sequence[str]] = None,
    ):
        self.server_url = server_url
        self.model = model
        self.imgsz = imgsz
        self.timeout = timeout
        self._names = tuple(names) if names else COCO_NAMES
        self._layout: Optional[str] = None  # 'raw' | 'end2end', from load()
        self._client = tc_grpc.InferenceServerClient(
            url=server_url, channel_options=_CHANNEL_OPTIONS
        )

    # ---- lifecycle --------------------------------------------------------

    def load(
        self,
        conf: float = 0.25,
        iou: float = 0.45,
        classes: Optional[Sequence[int]] = None,
        timeout_s: float = _READY_TIMEOUT_S,
    ):
        """Startup health gate: wait for the triton server, then run one
        end-to-end sanity inference so a broken model is caught here
        (not as silent zero-detections later). Not a model warm-up -
        triton's onnxruntime backend already warmed the model at load;
        we just prove the client-to-server path works and detect the
        output layout (raw vs end2end). Raises after timeout_s;
        main() treats that as an init failure."""
        gray = np.full((self.imgsz, self.imgsz, 3), _LETTERBOX_PAD, dtype=np.uint8)
        deadline = time.monotonic() + timeout_s
        attempt = 0
        while True:
            attempt += 1
            try:
                self.predict(gray, conf=conf, iou=iou, classes=classes)
                logger.info(
                    f"triton ready: {self.server_url} model={self.model} "
                    f"(sanity inference ok, layout={self._layout})"
                )
                return
            except Exception:
                if time.monotonic() >= deadline:
                    logger.error(
                        f"triton not ready at {self.server_url} after {timeout_s:.0f}s",
                        exc_info=True,
                    )
                    raise
                if attempt == 1 or attempt % 5 == 0:
                    logger.info(
                        f"triton not ready yet (attempt {attempt}) - "
                        f"retrying in 2s: {self.server_url}"
                    )
                time.sleep(2.0)

    # ---- inference --------------------------------------------------------

    def predict(
        self,
        frame: np.ndarray,
        conf: float = 0.25,
        iou: float = 0.45,
        classes: Optional[Sequence[int]] = None,
    ) -> TritonResult:
        """One frame -> TritonResult. Raises on transport / decode
        failure (the hot-path caller catches and backs off)."""
        tensor, meta = _letterbox(frame, self.imgsz)
        request = self._client.model_infer_request(
            self.model,
            inputs=[
                {"name": "images", "shape": list(tensor.shape), "data": tensor},
            ],
        )
        res = self._client.infer(self.model, request, timeout=self.timeout)
        out = np.asarray(res.get_tensor("output0"))
        if out.ndim == 3:
            out = out[0]
        return self._postprocess(out, meta, conf, iou, classes)

    # ---- post-processing --------------------------------------------------

    def _layout_of(self, shape: tuple) -> str:
        """(84, 8400)-ish = raw (anchor x (4+nc)); (N, 4..7) = end2end
        (max_det x (x1,y1,x2,y2,conf,cls[,pad]))."""
        return "raw" if shape[1] >= 1000 else "end2end"

    def _deletterbox(self, xyxy: np.ndarray, meta: dict) -> np.ndarray:
        """640-space xyxy -> full-frame pixels (inverse letterbox)."""
        r, top, left = meta["r"], meta["top"], meta["left"]
        x1 = (xyxy[:, 0] - left) / r
        y1 = (xyxy[:, 1] - top) / r
        x2 = (xyxy[:, 2] - left) / r
        y2 = (xyxy[:, 3] - top) / r
        return np.column_stack([x1, y1, x2, y2]).astype(np.float32)

    def _label(self, cls_id: int) -> str:
        names = self._names
        return names[cls_id] if 0 <= cls_id < len(names) else f"class_{cls_id}"

    def _postprocess(
        self,
        out: np.ndarray,
        meta: dict,
        conf: float,
        iou: float,
        classes: Optional[Sequence[int]],
    ) -> TritonResult:
        layout = self._layout_of(out.shape)
        if self._layout is None:
            self._layout = layout  # detected once (load's sanity inference)
        elif layout != self._layout:
            raise RuntimeError(
                f"triton output layout changed mid-run: {self._layout} -> {layout} "
                f"(out shape {out.shape}); the model file was swapped?"
            )

        if layout == "end2end":
            # x1,y1,x2,y2,conf,cls already NMS'd in the graph (640-space)
            rows = out
            sel = rows[:, 4] >= conf
            rows = rows[sel]
            if classes is not None:
                rows = rows[np.isin(rows[:, 5].astype(np.int64), np.asarray(list(classes)))]
            if not len(rows):
                return TritonResult(np.zeros((0, 5), np.float32), [])
            xyxy = self._deletterbox(rows[:, :4], meta)
            boxes = np.column_stack([xyxy, rows[:, 4]]).astype(np.float32)
            labels = [self._label(int(c)) for c in rows[:, 5]]
            return TritonResult(boxes, labels)

        # raw: out (84, 8400) -> (8400, 4+nc): cxywh in 640-space +
        # per-class sigmoid scores
        raw = out.T
        cxywh, scores = raw[:, :4], raw[:, 4:]
        top_cls = scores.argmax(axis=1)
        top_conf = scores.max(axis=1)
        sel = top_conf >= conf
        cxywh, top_conf, top_cls = cxywh[sel], top_conf[sel], top_cls[sel]
        kept = _nms(cxywh, top_conf, iou)
        if classes is not None:
            kept = kept[np.isin(top_cls[kept], np.asarray(list(classes)))]
        if not len(kept):
            return TritonResult(np.zeros((0, 5), np.float32), [])
        x1 = cxywh[kept, 0] - cxywh[kept, 2] / 2 - meta["left"]
        y1 = cxywh[kept, 1] - cxywh[kept, 3] / 2 - meta["top"]
        x2 = cxywh[kept, 0] + cxywh[kept, 2] / 2 - meta["left"]
        y2 = cxywh[kept, 1] + cxywh[kept, 3] / 2 - meta["top"]
        boxes = np.column_stack(
            [x1 / meta["r"], y1 / meta["r"], x2 / meta["r"], y2 / meta["r"], top_conf[kept]]
        ).astype(np.float32)
        labels = [self._label(int(c)) for c in top_cls[kept]]
        return TritonResult(boxes, labels)
