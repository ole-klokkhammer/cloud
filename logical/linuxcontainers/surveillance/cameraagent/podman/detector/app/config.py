"""Config for the detector service: env -> a typed, frozen Environment.

The LXC-side /env/surveillance/detector.env (wired into the container via
the quadlet unit's `EnvironmentFile=`) is the source of truth; this module
is the only place that reads it. main.py and detector.py do
`from config import environment` (attribute access: environment.triton_url,
environment.classes, ...) and own no config logic.

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
    classes: tuple | None
    frame_width: int
    input_size: int
    min_conf: float
    nms_iou: float
    class_names: tuple | None
    max_fps: float
    burst_window: float
    event_dir: str
    camera: str
    mqtt_host: str
    mqtt_port: int
    mqtt_topic: str
    mqtt_user: str
    mqtt_pass: str

    @property
    def classes_str(self) -> str:
        """Class filter as displayed (env/log): 'all' or a comma-separated
        list. The None<->'all' round-trip lives here, not in the users."""
        return "all" if self.classes is None else ",".join(map(str, self.classes))

    @classmethod
    def from_env(cls) -> "Environment":
        classes = _env_classes("DETECTOR_CLASS", "all")
        env = cls(
            rtsp_url=_env(
                "DETECTOR_RTSP_URL", "rtsp://mediamtx.homelan:8554/entrance_roof_sub"
            ),
            # inference runs in the triton container: the .onnx is served
            # there (from the LXC's /models), this process just talks gRPC
            triton_url=_env("DETECTOR_TRITON_URL", "http://127.0.0.1:8000"),
            triton_model=_env("DETECTOR_TRITON_MODEL", "detector"),
            classes=tuple(classes) if classes is not None else None,
            frame_width=_env_int("DETECTOR_FRAME_WIDTH", 1280),
            input_size=_env_int("DETECTOR_INPUT_SIZE", 640),
            min_conf=_env_float("DETECTOR_MIN_CONF", 0.5),
            nms_iou=_env_float("DETECTOR_NMS_IOU", 0.45),
            class_names=tuple(_env_class_names("DETECTOR_CLASS_NAMES")) or None,
            max_fps=_env_float("DETECTOR_MAX_FPS", 10),
            burst_window=_env_float("DETECTOR_BURST_WINDOW_SECS", 2.0),
            event_dir=_env("DETECTOR_EVENT_DIR", "/detections/events"),
            camera=_env("DETECTOR_CAMERA", "entrance_roof"),
            mqtt_host=_env("MQTT_HOST", "hivemq.homelan"),
            mqtt_port=_env_int("MQTT_PORT", 1883),
            mqtt_topic=_env("MQTT_TOPIC", "surveillance/detector"),
            mqtt_user=_env("MQTT_USER", ""),
            mqtt_pass=_env("MQTT_PASS", ""),
        )
        return env


environment = Environment.from_env()
