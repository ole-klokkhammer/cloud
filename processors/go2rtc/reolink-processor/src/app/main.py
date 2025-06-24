#!/usr/bin/python3

import logging
import cv2
import env as environment
import time
import os
import pandas as pd
from datetime import datetime

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")

logging.info("Starting Reolink Processor...")

snapshot_dir = "/home/ole/workspace/oleklokkhammer/projects/k3s/processors/go2rtc/reolink-processor/snapshots"
# os.makedirs(snapshot_dir, exist_ok=True)
snapshot_count = 0
static_back = None
motion_list = [None, None]
motion_times = []
fourcc = cv2.VideoWriter_fourcc(*"XVID")  # mp4v or 'XVID' for .avi
video_writer = None

motion_threshold = 500  # Minimum contour area to consider as motion
recording_frames = 20.0  # Number of frames to record after motion is detected
recording = False
min_record_time = 3
record_start_time = None
last_motion_time = None

max_failures = 10
failures = 0
background_update_interval = 10  # seconds
motion = False


os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp|stimeout;60000" 
video = cv2.VideoCapture(environment.stream_url)
try:
    while True:
        check, frame = video.read()

        if not check:
            failures += 1
            logging.warning(f"Failed to read from stream ({failures}/{max_failures})")
            if failures >= max_failures:
                logging.error("Max failures reached, attempting to reconnect...")
                video.release()
                logging.info("Waiting for 2 seconds before reconnecting...")
                time.sleep(2)
                video = cv2.VideoCapture(environment.stream_url)
                failures = 0
            continue
        failures = 0

        # Converts each frame to grayscale and applies Gaussian blur to reduce noise.
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (31, 31), 0)

        # Set static_back only once
        if static_back is None:
            static_back = gray
            cv2.imwrite(f"{snapshot_dir}/gray_{int(time.time())}.jpg", gray)
            cv2.imwrite(f"{snapshot_dir}/static_back_{int(time.time())}.jpg", static_back)
            continue

        # Computes the absolute difference between the current frame and the static background.
        diff_frame = cv2.absdiff(static_back, gray)

        # Threshold the difference to get binary image of motion areas
        _, thresh_frame = cv2.threshold(diff_frame, 50, 255, cv2.THRESH_BINARY)

        # Dilate to fill in holes and make contours more detectable
        thresh_frame = cv2.dilate(thresh_frame, None, iterations=2)

        # Find contours in the thresholded image
        cnts, _ = cv2.findContours(
            thresh_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        # reset motion state
        motion = False

        for contour in cnts:
            logging.debug(f"Contour area: {cv2.contourArea(contour) }")
            if cv2.contourArea(contour) < motion_threshold:
                continue
            logging.info("Motion detected")  
            motion = True
            last_motion_time = time.time() 
            break 

        if motion is True: 
            static_back = gray

            if video_writer is None:
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                video_filename = f"{snapshot_dir}/motion_{timestamp}.mp4"
                height, width = frame.shape[:2]
                video_writer = cv2.VideoWriter(
                    video_filename, fourcc, recording_frames, (width, height)
                )
                recording = True
                logging.info(f"Started recording: {video_filename}") 
        else:
            logging.debug("No motion detected")
            if last_motion_time is not None and (time.time() - last_motion_time > min_record_time):
                if video_writer is not None: 
                    video_writer.release()
                    video_writer = None
                    recording = False
                    logging.info("Stopped recording") 
       
        if recording is True and video_writer is not None:
            video_writer.write(frame)     
 
             
            
except KeyboardInterrupt:
    logging.info("Interrupted by user, shutting down...")
finally:
    if video_writer is not None:
        video_writer.release()
        logging.info("Video writer released.")
    if video is not None:
        video.release()
        logging.info("Video capture released.")  
