import logging
import pathlib
import uuid
import cv2
import time
import os
import numpy as np

from ai_edge_litert.interpreter import Interpreter, load_delegate

# import tflite_runtime.interpreter as tflite


class MotionDetector:
    def __init__(self, stream_url, kafka_producer=None, kafka_topic=None):
        self.stream_url = stream_url
        self.kafka_producer = kafka_producer
        self.kafka_topic = kafka_topic
        self.camera_id = stream_url

        self.failures = 0
        self.max_failures = 10

        self.recording = False
        self.kafka_frame_number = -1
        self.recording_id = None
        self.min_record_time = 3  # seconds

        self.last_motion_time = None
        self.video = None

    def shutdown(self, signum=None, frame=None):
        logging.info("Shutting down motion detection...")
        if self.kafka_producer is not None:
            self.kafka_producer.flush()
            self.kafka_producer.close()
            exit(0)

    def run(self):
        try:
            logging.info("Running motion detection...")

            logging.info("Loading model...")
            app_root = pathlib.Path(__file__).parent.parent.absolute()
            model_file = os.path.join(
                app_root,
                "models/mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite",
            )
            label_path = os.path.join(app_root, "models/coco_labels.txt")

            logging.info(f"Creating interpreter with model: {model_file}")
            model_file, *device = model_file.split("@")
            interpreter = Interpreter(
                model_path=model_file,
                experimental_delegates=[
                    load_delegate("libedgetpu.so.1", {"device": "usb"})
                ],
            )
            logging.info("Interpreter created successfully.")
            try:
                interpreter.allocate_tensors()
                logging.info("Tensors allocated successfully.")
            except Exception as e:
                logging.error(f"Failed to allocate tensors: {e}")
                raise e

            # # Get input and output details
            input_details = interpreter.get_input_details()
            output_details = interpreter.get_output_details()
            logging.debug(f"Input details: {input_details}")
            logging.debug(f"Output details: {output_details}")

            os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = (
                "rtsp_transport;tcp|stimeout;60000"
            )
            self.video = cv2.VideoCapture(self.stream_url)
            time.sleep(2)  # Allow time for the stream to stabilize

            fps = self.video.get(cv2.CAP_PROP_FPS) or 20.0
            width = int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))

            logging.info(
                f"Stream properties - FPS: {fps}, Width: {width}, Height: {height}"
            )

            while True:
                start_time = time.time()
                check, frame = self.video.read()
                read_duration = time.time() - start_time
                logging.debug(f"Time to read frame: {read_duration:.4f} seconds")

                if not self.handle_stream_failure(check):
                    continue

                # --- Inference on frame ---
                # 1. Resize frame to model input size
                input_shape = input_details[0]["shape"]
                height, width = input_shape[1], input_shape[2]
                frame_resized = cv2.resize(frame, (width, height))

                # 2. Convert to expected dtype (usually uint8)
                input_data = frame_resized.astype(input_details[0]["dtype"])

                # 3. Add batch dimension if needed
                if len(input_data.shape) == 3:
                    input_data = np.expand_dims(input_data, axis=0)

                # 4. Set input tensor
                interpreter.set_tensor(input_details[0]["index"], input_data)

                # 5. Run inference
                start = time.perf_counter()
                interpreter.invoke()
                inference_time = time.perf_counter() - start
                logging.info(f"Inference time: {inference_time * 1000:.1f} ms")

                # 6. Get output tensor
                output_data = interpreter.get_tensor(output_details[0]["index"])
                # logging.info(f"Inference result: {output_data}")
                motion_detected = True

                if motion_detected:
                    self.last_motion_time = time.time()
                    if self.recording is False:
                        self.start_recording()
                elif self.recording and self.last_motion_time is not None:
                    # Check if enough time has passed since the last motion
                    time_since_last_motion = time.time() - self.last_motion_time
                    time_left = max(0, self.min_record_time - time_since_last_motion)
                    logging.info(
                        f"No motion detected, stopping recording in {time_left:.2f} seconds."
                    )
                    if time_since_last_motion > self.min_record_time:
                        self.stop_recording()

                # if self.recording is True:
                # logging.info(
                #     "Recording: recording_id=%s, frame_number=%s",
                #     self.recording_id,
                #     self.kafka_frame_number,
                # )
                # self.kafka_frame_number += 1
                # self.send_frame_to_kafka(
                #     topic=self.kafka_topic,
                #     frame_number=self.kafka_frame_number,
                #     recording_id=self.recording_id,
                #     frame=frame,
                #     fps=fps,
                #     width=width,
                #     height=height,
                # )

        except KeyboardInterrupt:
            logging.info("Interrupted by user, shutting down...")
        finally:
            if self.video is not None:
                self.video.release()
                logging.info("Video capture released.")

    def start_recording(self):
        """
        Starts recording by setting the recording flag to True.
        This method can be called externally to start recording.
        """
        self.recording = True
        self.recording_id = uuid.uuid4()
        self.kafka_frame_number = -1
        logging.info("Recording started with ID: %s", self.recording_id)

    def stop_recording(self):
        """
        Stops recording by setting the recording flag to False.
        This method can be called externally to stop recording.
        """
        self.recording = False
        self.recording_id = None
        self.kafka_frame_number = 0
        logging.info("Recording stopped.")

    def send_frame_to_kafka(
        self, topic, frame_number, recording_id, frame, fps, width, height
    ):
        """
        Encodes the frame as JPEG and sends it to Kafka with appropriate headers.
        """
        if self.kafka_producer and self.kafka_topic:
            ret, buffer = cv2.imencode(".jpg", frame)
            if ret:
                future = self.kafka_producer.send(
                    topic,
                    value=buffer.tobytes(),
                    key=self.camera_id.encode("utf-8"),
                    headers=[
                        ("recording_id", str(recording_id).encode("utf-8")),
                        ("frame_number", str(frame_number).encode("utf-8")),
                        ("timestamp", str(time.time()).encode("utf-8")),
                        ("fps", str(fps).encode("utf-8")),
                        ("width", str(width).encode("utf-8")),
                        ("height", str(height).encode("utf-8")),
                        ("encoding", b"jpg"),
                    ],
                )
                future.add_callback(
                    lambda record_metadata: logging.debug(
                        f"Frame sent successfully: {record_metadata}"
                    )
                )
                future.add_errback(
                    lambda exc: logging.debug(f"Failed to send frame: {exc}")
                )
        else:
            logging.warning("Kafka producer or topic not set, skipping Kafka send.")

    def handle_stream_failure(self, check):
        """
        Handles video stream read failures and attempts reconnection if needed.
        Returns True if the stream is OK, False if it should continue to next loop.
        """
        if not check:
            self.failures += 1
            logging.warning(
                f"Failed to read from stream ({self.failures}/{self.max_failures})"
            )
            if self.failures >= self.max_failures:
                logging.error("Max failures reached, attempting to reconnect...")
                if self.video is not None:
                    self.video.release()
                logging.info("Waiting for 2 seconds before reconnecting...")
                time.sleep(2)
                self.video = cv2.VideoCapture(self.stream_url)
                self.failures = 0
            return False
        else:
            self.failures = 0
            return True
