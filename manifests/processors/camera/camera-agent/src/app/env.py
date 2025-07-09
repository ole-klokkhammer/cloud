#!/usr/bin/python3
import os

TRUTHY_VALUES = ("true", "1", "yes")
LOCAL_DEBUG = os.getenv("LOCAL_DEBUG", "False").lower() in TRUTHY_VALUES

log_level = os.environ.get("LOG_LEVEL", "INFO")

# CAMERA settings
camera_stream_url = os.getenv("CAMERA_STREAM_URL")

# OBJECT_DETECTOR settings
enable_object_detection = (
    os.getenv("ENABLE_OBJECT_DETECTION", "True").lower() in TRUTHY_VALUES
)
detector_frame_size = (640, 480)
object_detector_model_file = os.getenv(
    "OBJECT_DETECTOR_MODEL_FILE",
    "models/mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite",
)
object_detector_label_file = os.getenv(
    "OBJECT_DETECTOR_LABEL_FILE", "models/coco_labels.txt"
)

# RECORDER
recorder_storage_dir = os.getenv("RECORDER_STORAGE_DIR", "/data") 
recorder_frame_size = (1024, 768) 
recorder_fps = 10

# VIDEO RESTREAMER settings
enable_restreamer = os.getenv("ENABLE_VIDEO_RESTREAMER", "False").lower() in TRUTHY_VALUES
video_restreamer_stream_url =  os.getenv("VIDEO_RESTREAMER_STREAM_URL")
video_restreamer_frame_size = (640, 480)
video_restreamer_fps = 10