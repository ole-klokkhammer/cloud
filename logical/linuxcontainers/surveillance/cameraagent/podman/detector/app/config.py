"""Config for the detector service: env -> a typed, frozen Environment.

The LXC-side /env/surveillance/detector.env (wired into the container via
the quadlet unit's `EnvironmentFile=`) is the source of truth; this module
is the only place that reads it. main.py and detector.py do
`from config import environment` (attribute access: environment.model,
environment.classes, ...) and own no config logic.

Every variable has a default so the binary also runs with no env file at
all - but a production unit always ships the .env (see detector.env.example).
Bad values fail fast and name the offending variable instead of dying later
with a bare ValueError inside the capture loop.
"""

import os
from dataclasses import dataclass

_DEVICES = ("cuda", "cpu")


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


@dataclass(frozen=True)
class Environment:
    """Typed view of the detector's environment config (immutable -
    a frozen dataclass: no module can mutate the config mid-run)."""

    rtsp_url: str
    model: str
    classes: tuple | None
    frame_width: int
    input_size: int
    min_conf: float
    max_fps: float
    burst_window: float
    event_dir: str
    camera: str
    device: str
    nats_url: str
    nats_subject: str

    @property
    def classes_str(self) -> str:
        """Class filter as displayed (env/log): 'all' or a comma-separated
        list. The None<->'all' round-trip lives here, not in the users."""
        return "all" if self.classes is None else ",".join(map(str, self.classes))

    @classmethod
    def from_env(cls) -> "Environment":
        classes = _env_classes("DETECTOR_CLASS", "all")
        env = cls(
            rtsp_url=_env("DETECTOR_RTSP_URL", "rtsp://mediamtx.homelan:8554/entrance_roof_sub"),
            model=_env("DETECTOR_MODEL", "/models/yolo26m.pt"),
            classes=tuple(classes) if classes is not None else None,
            frame_width=_env_int("DETECTOR_FRAME_WIDTH", 1280),
            input_size=_env_int("DETECTOR_INPUT_SIZE", 640),
            min_conf=_env_float("DETECTOR_MIN_CONF", 0.5),
            max_fps=_env_float("DETECTOR_MAX_FPS", 10),
            burst_window=_env_float("DETECTOR_BURST_WINDOW_SECS", 2.0),
            event_dir=_env("DETECTOR_EVENT_DIR", "/detections/events"),
            camera=_env("DETECTOR_CAMERA", "entrance_roof"),
            device=_env("DETECTOR_DEVICE", "cuda"),
            nats_url=_env("NATS_URL", "nats://nats.homelan:4222"),
            nats_subject=_env("NATS_SUBJECT", "surveillance.detector"),
        )
        # cheap enum validation: a typo here used to be caught only after
        # the model had loaded (cost: a ~15s startup for the privilege)
        if env.device not in _DEVICES:
            raise SystemExit(
                f"[detector] DETECTOR_DEVICE={env.device!r} - expected one of {_DEVICES}"
            )
        return env


environment = Environment.from_env()
