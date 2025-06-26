import numpy as np
import cv2


# https://github.com/itberrios/CV_projects/blob/main/motion_detection/motion_detection_utils.py
class BackgroundSubtractorMOG2:
    def __init__(
            self, 
            history=100, 
            varThreshold=5, 
            detectShadows=True, 
            shadowThreshold=0.5
        ):
        self.bg_sub = cv2.createBackgroundSubtractorMOG2(
            history=history, varThreshold=varThreshold, detectShadows=detectShadows
        )
        self.bg_sub.setShadowThreshold(shadowThreshold)  

    def reset(self):
        """Resets the background subtraction model."""
        self.bg_sub.reset()

    def get_detections(
        self, 
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
        fg_mask = self.bg_sub.apply(frame)

        # get clean motion mask
        motion_mask = self.get_motion_mask(fg_mask, kernel=kernel)

        # get initially proposed detections from contours
        detections = self.get_contour_detections(motion_mask, bbox_thresh)

        if detections.size == 0:
            return np.array([])
        else:
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
