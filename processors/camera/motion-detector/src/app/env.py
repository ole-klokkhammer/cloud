#!/usr/bin/python3
import os

LOCAL_DEBUG = os.getenv("LOCAL_DEBUG", "False").lower() in ("true", "1", "yes")
log_level = os.environ.get("LOG_LEVEL", "INFO")


enable_object_detection = os.getenv("ENABLE_OBJECT_DETECTION", "True").lower() in (
    "true",
    "1",
    "yes",
)
enable_kafka = os.getenv("ENABLE_KAFKA", "True").lower() in ("true", "1", "yes")
enable_restreamer = os.getenv("ENABLE_RESTREAMER", "False").lower() in (
    "true",
    "1",
    "yes",
)


entrance_roof_stream_url = os.getenv("ENTRANCE_ROOF_STREAM_URL")
motion_detector_frame_width = 640
motion_detector_frame_height = 480
restreamer_fps = int(os.getenv("DETECTION_FPS", "10"))
restreamer_stream_name="entrance_roof"


kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
kafka_topic = os.getenv("KAFKA_TOPIC")

object_detector_model_file = os.getenv(
    "OBJECT_DETECTOR_MODEL_FILE",
    "models/mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite",
)
object_detector_label_file = os.getenv(
    "OBJECT_DETECTOR_LABEL_FILE", "models/coco_labels.txt"
)
