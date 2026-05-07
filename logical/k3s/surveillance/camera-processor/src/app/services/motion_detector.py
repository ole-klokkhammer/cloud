#!/usr/bin/python3

from dataclasses import dataclass
import logging
from typing import Optional
import numpy as np
import cv2
from services.object_detector import CoralTPUObjectDetectorService
from utils.bg_subtractor_mog2 import BackgroundSubtractorMOG2
from app.processors.stream_processor import FrameEvent, MotionData
from types.frame import OnFrameCallback


logger = logging.getLogger(__name__)


class MotionDetectorService:
    def __init__(
        self,
        detector_frame_size: tuple,
        model_file: str,
        label_file: str,
        enable_object_detection: bool,
    ):
        self.motion_callback: Optional[OnFrameCallback] = None
        self.detector_frame_size = detector_frame_size
        self.enable_object_detection = enable_object_detection

        self.background_subtractor = BackgroundSubtractorMOG2(
            history=100, varThreshold=5, detectShadows=True, shadowThreshold=0.5
        )

        self.object_detector = CoralTPUObjectDetectorService(
            model_file=model_file,
            label_file=label_file,
        )

        if self.enable_object_detection:
            self.object_detector.initialize()

    def process(self, event: FrameEvent):
        frame = event.frame
        detected_motions = np.empty((0, 6), dtype=np.float32)
        detected_objects = np.empty((0, 6), dtype=np.float32)

        detector_frame = cv2.cvtColor(
            cv2.resize(
                frame,
                self.detector_frame_size,
            ),
            cv2.COLOR_BGR2GRAY,
        )
        detected_motions = self.background_subtractor.get_detections(detector_frame)
        motion_detected = detected_motions.size > 0

        if motion_detected:
            if self.enable_object_detection:
                detected_objects = self.object_detector.detect_objects(detector_frame)

            event.motion = MotionData(
                detected_motions=detected_motions,
                detected_objects=detected_objects,
            )
            if self.motion_callback:
                self.motion_callback(event)

    def set_motion_callback(self, frame_callback: OnFrameCallback):
        self.motion_callback = frame_callback
        return self
