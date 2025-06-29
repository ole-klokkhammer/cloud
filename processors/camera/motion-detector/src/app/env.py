#!/usr/bin/python3
import os

TRUTHY_VALUES = ("true", "1", "yes")
LOCAL_DEBUG = os.getenv("LOCAL_DEBUG", "False").lower() in TRUTHY_VALUES

log_level = os.environ.get("LOG_LEVEL", "INFO")
enable_object_detection = (
    os.getenv("ENABLE_OBJECT_DETECTION", "True").lower() in TRUTHY_VALUES
)
enable_restreamer = os.getenv("ENABLE_RESTREAMER", "False").lower() in TRUTHY_VALUES

# KAFKA settings
kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
kafka_topic = os.getenv("KAFKA_TOPIC")

# object detector settings
object_detector_model_file = os.getenv(
    "OBJECT_DETECTOR_MODEL_FILE",
    "models/mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite",
)
object_detector_label_file = os.getenv(
    "OBJECT_DETECTOR_LABEL_FILE", "models/coco_labels.txt"
)

# entrance roof camera settings
entrance_roof_stream_url = os.getenv("ENTRANCE_ROOF_STREAM_URL")
entrance_roof_detector_frame_size = (640, 480)
entrance_roof_output_fps = int(os.getenv("ENTRANCE_ROOF_FPS", "10"))
entrance_roof_output_frame_size = entrance_roof_detector_frame_size
