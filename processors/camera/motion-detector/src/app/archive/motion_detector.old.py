import logging
import pathlib
import uuid
import cv2
import time
import os
import numpy as np
 


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

    def run(self):
        try:
            logging.info("Running motion detection...")
 

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

            bg_sub = cv2.createBackgroundSubtractorMOG2(
                history=100, varThreshold=16, detectShadows=True
            )

            while True:
                start_time = time.time()
                check, frame = self.video.read()
                read_duration = time.time() - start_time
                logging.debug(f"Time to read frame: {read_duration:.4f} seconds")

                if not self.handle_stream_failure(check):
                    continue
 
                self.detections = self.get_detections(
                    bg_sub,
                    frame,
                    bbox_thresh=100,
                    nms_thresh=1e-2,
                    kernel=np.array((9, 9), dtype=np.uint8),
                )
                logging.info(f"Detections: {self.detections}")

 
                
                threshold = 0.2
                motion_detected = False
                for i in range(int(num_detections[0])):
                    if scores[0][i] > threshold:
                        motion_detected = True
                        break

                # logging.info(f"Object detected: {motion_detected}")

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
                #     logging.info(
                #         "Recording: recording_id=%s, frame_number=%s",
                #         self.recording_id,
                #         self.kafka_frame_number,
                #     )
                #     self.kafka_frame_number += 1
                #     self.send_frame_to_kafka(
                #         topic=self.kafka_topic,
                #         frame_number=self.kafka_frame_number,
                #         recording_id=self.recording_id,
                #         frame=frame,
                #         fps=fps,
                #         width=width,
                #         height=height,
                #     )

        except KeyboardInterrupt:
            logging.info("Interrupted by user, shutting down...")
        finally:
            if self.video is not None:
                self.video.release()
                logging.info("Video capture released.")

    def get_detections(
        self,
        backSub,
        frame,
        bbox_thresh=100,
        nms_thresh=0.1,
        kernel=np.array((9, 9), dtype=np.uint8),
    ):
        """Main function to get detections via Frame Differencing
        Inputs:
            backSub - Background Subtraction Model
            frame - Current BGR Frame
            bbox_thresh - Minimum threshold area for declaring a bounding box
            nms_thresh - IOU threshold for computing Non-Maximal Supression
            kernel - kernel for morphological operations on motion mask
        Outputs:
            detections - list with bounding box locations of all detections
                bounding boxes are in the form of: (xmin, ymin, xmax, ymax)
        """
        # Update Background Model and get foreground mask
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        fg_mask = backSub.apply(gray_frame)

        # get clean motion mask
        motion_mask = self.get_motion_mask(fg_mask, kernel=kernel)

        # get initially proposed detections from contours
        detections = self.get_contour_detections(motion_mask, bbox_thresh)

        if detections.size == 0:
            return np.array([])
        

        # separate bboxes and scores
        bboxes = detections[:, :4]
        scores = detections[:, -1]

        # perform Non-Maximal Supression on initial detections
        return self.non_max_suppression(bboxes, scores, nms_thresh)

    def get_motion_mask(
        self, fg_mask, min_thresh=0, kernel=np.array((9, 9), dtype=np.uint8)
    ):
        """Obtains image mask
        Inputs:
            fg_mask - foreground mask
            kernel - kernel for Morphological Operations
        Outputs:
            mask - Thresholded mask for moving pixels
        """
        _, thresh = cv2.threshold(fg_mask, min_thresh, 255, cv2.THRESH_BINARY)
        motion_mask = cv2.medianBlur(thresh, 3)

        # morphological operations
        motion_mask = cv2.morphologyEx(
            motion_mask, cv2.MORPH_OPEN, kernel, iterations=1
        )
        motion_mask = cv2.morphologyEx(
            motion_mask, cv2.MORPH_CLOSE, kernel, iterations=1
        )

        return motion_mask

    def get_contour_detections(self, mask, thresh=400):
        """Obtains initial proposed detections from contours discoverd on the
        mask. Scores are taken as the bbox area, larger is higher.
        Inputs:
            mask - thresholded image mask
            thresh - threshold for contour size
        Outputs:
            detectons - array of proposed detection bounding boxes and scores
                        [[x1,y1,x2,y2,s]]
        """
        # get mask contours
        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1  # cv2.RETR_TREE,
        )
        detections = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            area = w * h
            if area > thresh:  # hyperparameter
                detections.append([x, y, x + w, y + h, area])

        return np.array(detections)

    def non_max_suppression(self, boxes, scores, threshold=1e-1):
        """
        Perform non-max suppression on a set of bounding boxes
        and corresponding scores.
        Inputs:
            boxes: a list of bounding boxes in the format [xmin, ymin, xmax, ymax]
            scores: a list of corresponding scores
            threshold: the IoU (intersection-over-union) threshold for merging bboxes
        Outputs:
            boxes - non-max suppressed boxes
        """
        # Sort the boxes by score in descending order
        boxes = boxes[np.argsort(scores)[::-1]]

        # remove all contained bounding boxes and get ordered index
        order = self.remove_contained_bboxes(boxes)

        keep = []
        while order:
            i = order.pop(0)
            keep.append(i)
            for j in order:
                # Calculate the IoU between the two boxes
                intersection = max(
                    0, min(boxes[i][2], boxes[j][2]) - max(boxes[i][0], boxes[j][0])
                ) * max(
                    0, min(boxes[i][3], boxes[j][3]) - max(boxes[i][1], boxes[j][1])
                )
                union = (
                    (boxes[i][2] - boxes[i][0]) * (boxes[i][3] - boxes[i][1])
                    + (boxes[j][2] - boxes[j][0]) * (boxes[j][3] - boxes[j][1])
                    - intersection
                )
                iou = intersection / union

                # Remove boxes with IoU greater than the threshold
                if iou > threshold:
                    order.remove(j)

        return boxes[keep]

    def remove_contained_bboxes(self, boxes):
        """Removes all smaller boxes that are contained within larger boxes.
        Requires bboxes to be soirted by area (score)
        Inputs:
            boxes - array bounding boxes sorted (descending) by area
                    [[x1,y1,x2,y2]]
        Outputs:
            keep - indexes of bounding boxes that are not entirely contained
                in another box
        """
        check_array = np.array([True, True, False, False])
        keep = list(range(0, len(boxes)))
        for i in keep:  # range(0, len(bboxes)):
            for j in range(0, len(boxes)):
                # check if box j is completely contained in box i
                if np.all((np.array(boxes[j]) >= np.array(boxes[i])) == check_array):
                    try:
                        keep.remove(j)
                    except ValueError:
                        continue
        return keep

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
