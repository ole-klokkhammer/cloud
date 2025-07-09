import logging
import os
import pathlib
import time
from typing import Protocol

import numpy as np
import cv2
from ai_edge_litert.interpreter import Interpreter, load_delegate

logger = logging.getLogger(__name__)

class CoralTPUObjectDetectorService:
    def __init__(
        self,
        model_file="mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite",
        label_file="coco_labels.txt",
    ): 
        app_root = pathlib.Path(__file__).parent.parent.absolute()
        self.model_file_path = os.path.join(
            app_root,
            f"models/{model_file}",
        )
        self.label_path = os.path.join(app_root, f"models/{label_file}")
        self.input_details = None
        self.output_details = None

    def initialize(self):
        try:
            logger.info(f"Initializing Coral TPU with model: {self.model_file_path}")
            self.interpreter = Interpreter(
                model_path=self.model_file_path,
                experimental_delegates=[
                    load_delegate("libedgetpu.so.1", {"device": "usb"})
                ],
            ) 
            self.interpreter.allocate_tensors()
            logger.info("Tensors allocated successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Coral TPU: {e}")
            raise e 

    def detect_objects(self, frame: cv2.UMat):
        logger.info("Motion detected, processing frame...")

        # do some object detection if enabled
        object_detections = np.empty((0, 6), dtype=np.float32)  
        # if environment.enable_object_detection:
        #     try:
        #         object_detections = self.object_detector.detect_objects(
        #             frame=self.get_detection_frame(frame)
        #         )
        #     except Exception as e:
        #         logger.error(f"Object detection failed: {e}")
        return object_detections

    def inference(self, frame):
        # --- Inference on frame ---
        # input
        self.input_details = self.interpreter.get_input_details()
        self.input_shape = self.input_details[0]["shape"]
        self.d_shape = self.input_shape[0]["dtype"]
        self.height = self.input_shape[1]
        self.width = self.input_shape[2]
        self.input_tensor_index = self.input_details[0]["index"]

        # output
        self.output_details = self.interpreter.get_output_details()
        self.output_tensor_boxes = self.output_details[0]["index"]
        self.output_tensor_classes = self.output_details[1]["index"]
        self.output_tensor_scores = self.output_details[2]["index"]
        self.output_tensor_num_detections = self.output_details[3]["index"]

        # 1. Resize frame to model input size
        frame_resized = cv2.resize(frame, (self.width, self.height))

        # 2. Convert to expected dtype (usually uint8)
        input_data = frame_resized.astype(self.d_shape)

        # 3. Add batch dimension if needed
        if len(input_data.shape) == 3:
            input_data = np.expand_dims(input_data, axis=0)

        # 4. Set input tensor
        self.interpreter.set_tensor(self.input_tensor_index, input_data)

        # 5. Run inference
        start = time.perf_counter()
        self.interpreter.invoke()
        inference_time = time.perf_counter() - start
        logging.debug(f"Inference time: {inference_time * 1000:.1f} ms")  

    def get_boxes(self):
        return self.interpreter.get_tensor(self.output_tensor_boxes)

    def get_classes(self):
        return self.interpreter.get_tensor(self.output_tensor_classes)

    def get_scores(self):
        return self.interpreter.get_tensor(self.output_tensor_scores)

    def get_num_detections(self):
        return self.interpreter.get_tensor(self.output_tensor_num_detections)
