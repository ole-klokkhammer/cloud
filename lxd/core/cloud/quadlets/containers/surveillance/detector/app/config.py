"""Config for the detector service: env -> a typed, frozen Environment.

The LXC-side /env/surveillance/detector.env (wired into the container via
the quadlet unit's `EnvironmentFile=`) is the source of truth; this module
is the only place that reads it. main.py and detector.py do
`from config import environment` (attribute access: environment.triton_url,
environment.class_filter, ...) and own no config logic.

Every variable has a default so the binary also runs with no env file at
all - but a production unit always ships the .env (see detector.env.example).
Bad values fail fast and name the offending variable instead of dying later
with a bare ValueError inside the capture loop.
"""

import os
from dataclasses import dataclass


def _env(name, default):
    return os.environ.get(name, default)


def _env_int(name, default):
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        raise SystemExit(f"[detector] {name}={raw!r} is not an integer")


def _env_float(name, default):
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        raise SystemExit(f"[detector] {name}={raw!r} is not a number")


def _env_labels(name, default):
    """Comma-separated model class NAMES to track (persistent ids across
    frames): DETECTOR_TRACK_LABELS=person,cat. Names, not ids - ids
    depend on the model's export, names don't."""
    raw = os.environ.get(name, default)
    toks = [t.strip().lower() for t in raw.split(",") if t.strip()]
    if not toks:
        raise SystemExit(f"[detector] {name}={raw!r}: empty name list")
    return tuple(toks)


def _env_classes(name, default):
    """Class filter for predict(): comma-separated COCO class ids
    (DETECTOR_CLASS=15 or 15,16,24) or the keyword 'all' = no class
    filter (any of the 80 COCO classes)."""
    raw = os.environ.get(name, default)
    toks = [t.strip() for t in raw.split(",") if t.strip()]
    if "all" in toks:
        if toks != ["all"]:
            raise SystemExit(
                f"[detector] {name}={raw!r}: 'all' means no filter and "
                f"cannot be mixed with class ids"
            )
        return None
    out = []
    for tok in toks:
        try:
            out.append(int(tok))
        except ValueError:
            raise SystemExit(f"[detector] {name}={raw!r}: {tok!r} is not an integer")
    if not out:
        raise SystemExit(
            f"[detector] {name}={raw!r}: no class ids given (use 'all' for no filter)"
        )
    return out


def _env_family(name, default="yolo"):
    """Model I/O contract family: 'yolo' (letterbox input, raw/end2end
    output, client-side NMS for raw) or 'rtdetr' (stretch input,
    [300,6] normalized cxywh output, NMS in the graph). Must match the
    model the triton server serves - the wrong family = off/clustered
    boxes, not an error (the client can't tell the two [300,6] layouts
    apart by shape alone)."""
    raw = os.environ.get(name, default).strip().lower()
    if raw not in ("yolo", "rtdetr"):
        raise SystemExit(f"[detector] {name}={raw!r} must be 'yolo' or 'rtdetr'")
    return raw


def _env_class_names(name, default=""):
    """Optional class-name override for fine-tuned models: a
    comma-separated list of names (index = class id). Empty = use the
    built-in COCO names in triton_client.py."""
    raw = os.environ.get(name, default)
    toks = [t.strip() for t in raw.split(",") if t.strip()]
    return toks


@dataclass(frozen=True)
class Environment:
    """Typed view of the detector's environment config (immutable -
    a frozen dataclass: no module can mutate the config mid-run)."""

    rtsp_url: str
    triton_url: str
    triton_model: str
    triton_input_size: int
    triton_class_filter: tuple | None
    triton_class_labels: tuple | None
    triton_min_conf: float
    triton_iou: float
    triton_model_family: str
    detector_max_fps: float
    detector_burst_window: float
    detector_live_path: str
    detector_live_hold: float
    tracker_labels: tuple
    event_camera_name: str
    mqtt_host: str
    mqtt_port: int
    mqtt_topic: str
    mqtt_user: str
    mqtt_pass: str

    @property
    def class_filter_str(self) -> str:
        """Class filter as displayed (env/log): 'all' or a comma-separated
        list. The None<->'all' round-trip lives here, not in the users."""
        return (
            "all"
            if self.triton_class_filter is None
            else ",".join(map(str, self.triton_class_filter))
        )


_detected_class_filter = _env_classes("TRITON_CLASS_FILTER", "all")
triton_class_filter = (
    tuple(_detected_class_filter) if _detected_class_filter is not None else None
)
triton_class_labels = tuple(_env_class_names("TRITON_CLASS_NAMES")) or None

environment = Environment(
    rtsp_url=_env("RTSP_URL", "rtsp://mediamtx.homelan:8554/entrance_roof_sub"),
    triton_url=_env("TRITON_URL", "http://127.0.0.1:8000"),
    triton_model=_env("TRITON_MODEL", "detector"),
    triton_class_filter=triton_class_filter,
    triton_class_labels=triton_class_labels,
    triton_input_size=_env_int("TRITON_INPUT_SIZE", 640),
    triton_min_conf=_env_float("TRITON_MIN_CONF", 0.5),
    triton_iou=_env_float("TRITON_IOU", 0.45),
    triton_model_family=_env_family("TRITON_MODEL_FAMILY", "yolo"),
    detector_max_fps=_env_float("DETECTOR_MAX_FPS", 10),
    detector_burst_window=_env_float("DETECTOR_BURST_WINDOW_SECS", 2.0),
    tracker_labels=_env_labels("DETECTOR_TRACK_LABELS", "person,cat"),
    # the annotated RTSP push into mediaMTX (path auto-created on publish);
    # empty = the live push is disabled
    detector_live_path=_env("DETECTOR_LIVE_PATH", ""),
    detector_live_hold=_env_float("DETECTOR_LIVE_HOLD_SECONDS", 3),
    event_camera_name=_env("EVENT_CAMERA_NAME", "entrance_roof"),
    mqtt_host=_env("MQTT_HOST", "hivemq.homelan"),
    mqtt_port=_env_int("MQTT_PORT", 1883),
    mqtt_topic=_env("MQTT_TOPIC", "surveillance/detector"),
    mqtt_user=_env("MQTT_USER", ""),
    mqtt_pass=_env("MQTT_PASS", ""),
)
