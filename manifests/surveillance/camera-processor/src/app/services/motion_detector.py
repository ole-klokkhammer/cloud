#!/usr/bin/python3

import logging
import numpy as np
import cv2
from services.object_detector import CoralTPUObjectDetectorService
from utils.bg_subtractor_mog2 import BackgroundSubtractorMOG2
from processors.video_processor import FrameEvent, MotionData

logger = logging.getLogger(__name__)


class MotionDetectorService:
    def __init__(
        self,
        detector_frame_size: tuple,
        model_file: str,
        label_file: str,
        enable_object_detection: bool,
    ):
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
        if detected_motions.size > 0:
            if self.enable_object_detection:
                detected_objects = self.object_detector.detect_objects(detector_frame)

        event.motion = MotionData(
            detected_motions=detected_motions,
            detected_objects=detected_objects,
        )
