#!/usr/bin/python3
 
import logging  
import cv2
import env as environment
from services.object_detector import CoralTPUObjectDetectorService
from services.camera_reader import CameraReaderService
from services.video_recorder import VideoRecorderService
from services.video_restreamer import VideoRestreamerService
from utils.bg_subtractor_mog2 import BackgroundSubtractorMOG2 


class MotionDetectorService:
    def __init__(self): 
        self.detector_frame_size = environment.detector_frame_size 

        self.camera_reader = CameraReaderService(
            stream_url=environment.camera_stream_url, 
            on_frame=self.on_frame
        )
        self.video_recorder = VideoRecorderService(
            fps=environment.recorder_fps,
            frame_size=environment.recorder_frame_size,
            storage_dir=environment.recorder_storage_dir,
        )
        self.background_subtractor = BackgroundSubtractorMOG2(
            history=100, varThreshold=5, detectShadows=True, shadowThreshold=0.5
        )  

        # Initialize the object detector if enabled
        if environment.enable_object_detection:
            logging.info("Object detection is enabled.")
            self.object_detector = CoralTPUObjectDetectorService(
                model_file=environment.object_detector_model_file,
                label_file=environment.object_detector_label_file,
            )
        else:
            logging.info("Object detection is disabled.")
            self.object_detector = None

        # Initialize the restreamer if enabled
        if environment.enable_restreamer:
            logging.info("Restreamer is enabled.")
            self.video_restreamer = VideoRestreamerService(
                stream_url=environment.video_restreamer_stream_url,
                frame_size=environment.video_restreamer_frame_size,
                fps=environment.video_restreamer_fps,
            )
        else:
            logging.info("Restreamer is disabled.")
            self.video_restreamer = None

    def start(self):
        try:
            logging.info("Starting motion detector...")

            logging.info("Starting video recorder...")
            self.video_recorder.start()
            logging.info("Video recorder started successfully.")

            logging.info("Starting camera reader...")
            self.camera_reader.start()
            logging.info("Video reader started successfully.")
            
            # start the object detector if it is configured
            if self.object_detector is not None:
                logging.info("Initializing object detector...")
                self.object_detector.initialize()
                logging.info("Object detector initialized successfully.")
            else:
                logging.warning(
                    "Object detector is not configured, skipping initialization."
                )

            # start the video restreamer if it is configured
            if self.video_restreamer is not None:
                logging.info("Starting video_restreamer")
                self.video_restreamer.start()
            else:
                logging.info(
                    "Restreamer is not configured, skipping FFmpeg subprocess."
                )
        except KeyboardInterrupt:
            logging.info("Interrupted by user, shutting down...")
        except Exception as e:
            logging.error(f"An error occurred: {e}")
        finally:
            self.stop()

    def stop(self):
        try:
            logging.info("Shutting down motion detection...")
            self.camera_reader.stop()
            self.video_recorder.stop() 

            if self.video_restreamer is not None:
                self.video_restreamer.stop()
        except Exception as e:
            logging.error(f"Error during shutdown: {e}")

    def on_frame(self, original_frame: cv2.UMat):
        detection_frame = cv2.cvtColor(
            cv2.resize(
                original_frame,
                self.detector_frame_size,
            ),
            cv2.COLOR_BGR2GRAY,
        )
        detections = self.background_subtractor.get_detections(detection_frame)

        if detections.size > 0:
            logging.info(f"Detected {len(detections)} objects in the frame.")
            self.video_recorder.write_frame(
                frame=original_frame,
                detections=detections,
                detection_frame_size=self.detector_frame_size,
            )

            if self.video_restreamer is not None:
                self.video_restreamer.write_frame(
                    frame=original_frame,
                    detections=detections,
                    detection_frame_size=self.detector_frame_size,
                )
 