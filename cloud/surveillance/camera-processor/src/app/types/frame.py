from dataclasses import dataclass
import numpy as np
import cv2
from typing import Protocol


@dataclass
class MotionData:
    detected_motions: np.ndarray = np.empty((0, 6), dtype=np.float32)
    detected_objects: np.ndarray = np.empty((0, 6), dtype=np.float32)


@dataclass
class FrameEvent:
    frame: cv2.UMat
    frame_size: tuple[int, int]
    timestamp: float
    fps: int
    motion: MotionData


class OnFrameCallback(Protocol):
    def __call__(self, event: FrameEvent):
        None
