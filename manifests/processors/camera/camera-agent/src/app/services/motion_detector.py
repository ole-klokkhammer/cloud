#!/usr/bin/python3

import logging
from typing import Protocol
import numpy as np
import cv2
import env as environment
from services.object_detector import CoralTPUObjectDetectorService
from utils.bg_subtractor_mog2 import BackgroundSubtractorMOG2
from processors.video_processor import FrameEvent
from dataclasses import dataclass


@dataclass
class MotionEvent:
    frame_event: FrameEvent
    detector_frame: cv2.UMat
    detected_motions: np.ndarray
    detected_objects: np.ndarray


class OnMotionCallback(Protocol):
    def __call__(self, event: MotionEvent):
        None


logger = logging.getLogger(__name__)


class MotionDetectorService:
    def __init__(self):
        self.listeners: list[OnMotionCallback] = []
        self.detector_frame_size = environment.detector_frame_size

        self.background_subtractor = BackgroundSubtractorMOG2(
            history=100, varThreshold=5, detectShadows=True, shadowThreshold=0.5
        )

        self.object_detector = CoralTPUObjectDetectorService(
            model_file=environment.object_detector_model_file,
            label_file=environment.object_detector_label_file,
        )

        if environment.enable_object_detection:
            self.object_detector.initialize()

    def add_listener(self, listener: OnMotionCallback):
        """Register a callback to be called on output events."""
        self.listeners.append(listener)

    def on_frame(self, event: FrameEvent):
        detector_frame = cv2.cvtColor(
            cv2.resize(
                event.frame,
                self.detector_frame_size,
            ),
            cv2.COLOR_BGR2GRAY,
        )
        detected_motions = self.background_subtractor.get_detections(detector_frame)

        if detected_motions.size > 0:
            detected_objects = np.empty((0, 6), dtype=np.float32)
            if environment.enable_object_detection:
                detected_objects = self.object_detector.detect_objects(detector_frame)

            for on_motion in self.listeners:
                on_motion(
                    event=MotionEvent(
                        frame_event=event,
                        detector_frame=detector_frame.copy(),
                        detected_motions=detected_motions.copy(),
                        detected_objects=detected_objects.copy(),
                    )
                )
