import cv2
import os
import numpy as np
from datetime import datetime
from typing import Tuple, Union, Any

from ANPRmodel.errors.errors import AakashError
#from ANPRmodel.errors.errors import VideoStreamError

def record(video_feed: Union[str, int], 
          save_path: str = os.path.join('ANPRmodel', 'testing', 'test_data', f'{datetime.now()}.mp4')) -> int:
    """
    Record video from a feed and save it to specified path.
    
    Args:
        video_feed: Path to video file or camera index
        save_path: Path where the recorded video will be saved
    
    Returns:
        0 if successful
    
    Raises:
        AakashError: If video capture fails
    """
    video = cv2.VideoCapture(video_feed)

    if not video.isOpened():
        raise AakashError("Failed to open video feed")

    frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    result = cv2.VideoWriter(
        save_path,
        cv2.VideoWriter_fourcc(*'MJPG'),
        10,
        (frame_width, frame_height)
    )

    print("Press 's' to stop recording")
    
    try:
        while True:
            ret, frame = video.read()
            if not ret:
                break

            result.write(frame)
            cv2.imshow('Frame', frame)

            if cv2.waitKey(1) & 0xFF == ord('s'):
                break
    finally:
        video.release()
        result.release()
        cv2.destroyAllWindows()
    
    return 0

def four_point_transform(image: np.ndarray, x1: int, x2: int, y1: int, y2: int) -> np.ndarray:
    """
    Transform a region of an image using perspective transform.
    
    Args:
        image: Input image
        x1, x2, y1, y2: Coordinates defining the region
    
    Returns:
        Transformed image
    """
    # Create points array
    pts = np.array([
        [x1, y2],  # top-left
        [x2, y2],  # top-right
        [x2, y1],  # bottom-right
        [x1, y1]   # bottom-left
    ], dtype="float32")

    rect = order_points(pts)
    
    # Calculate dimensions
    widthA = np.sqrt(((rect[2][0] - rect[3][0]) ** 2) + ((rect[2][1] - rect[3][1]) ** 2))
    widthB = np.sqrt(((rect[1][0] - rect[0][0]) ** 2) + ((rect[1][1] - rect[0][1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    heightA = np.sqrt(((rect[1][0] - rect[2][0]) ** 2) + ((rect[1][1] - rect[2][1]) ** 2))
    heightB = np.sqrt(((rect[0][0] - rect[3][0]) ** 2) + ((rect[0][1] - rect[3][1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]
    ], dtype="float32")

    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    return warped

def order_points(pts: np.ndarray) -> np.ndarray:
    """
    Order points in clockwise order starting from top-left.
    
    Args:
        pts: Array of 4 points
    
    Returns:
        Ordered points array
    """
    # initialzie a list of coordinates that will be ordered
    # such that the first entry in the list is the top-left,
    # the second entry is the top-right, the third is the
    # bottom-right, and the fourth is the bottom-left
    rect = np.zeros((4, 2), dtype = "float32")
    # the top-left point will have the smallest sum, whereas
    # the bottom-right point will have the largest sum
    s = pts.sum(axis = 1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    # now, compute the difference between the points, the
    # top-right point will have the smallest difference,
    # whereas the bottom-left will have the largest difference
    diff = np.diff(pts, axis = 1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    # return the ordered coordinates
    return rect