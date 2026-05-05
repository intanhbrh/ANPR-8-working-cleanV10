import cv2
import time
import logging

class VideoStream:
    def __init__(self, source, retry_interval=3, max_retries=None):
        self.source = source
        self.retry_interval = retry_interval
        self.max_retries = max_retries
        self.cap = None
        self.retry_count = 0
        self.last_reconnect = 0
        self.logger = logging.getLogger(__name__)
        self.connect()

    def connect(self):
        """Attempt to connect to the video stream"""
        try:
            if self.cap is not None:
                self.cap.release()
            
            self.cap = cv2.VideoCapture(self.source)
            if not self.cap.isOpened():
                raise ConnectionError("Failed to open video stream")
            
            self.retry_count = 0
            self.logger.info("Successfully connected to video stream")
            return True
        except Exception as e:
            self.logger.error(f"Connection failed: {str(e)}")
            return False

    def reconnect(self):
        """Attempt to reconnect to the video stream"""
        current_time = time.time()
        if current_time - self.last_reconnect < self.retry_interval:
            return False

        self.last_reconnect = current_time
        self.retry_count += 1
        
        if self.max_retries and self.retry_count > self.max_retries:
            self.logger.error("Max reconnection attempts reached")
            return False

        self.logger.info(f"Attempting reconnection (attempt {self.retry_count})")
        return self.connect()

    def read(self):
        """Read a frame from the video stream with auto-reconnection"""
        if not self.cap or not self.cap.isOpened():
            if not self.reconnect():
                return False, None
        
        try:
            ret, frame = self.cap.read()
            if not ret:
                self.logger.warning("Failed to read frame, attempting reconnection")
                if self.reconnect():
                    return self.read()
                return False, None
            return True, frame
        except Exception as e:
            self.logger.error(f"Error reading frame: {str(e)}")
            if self.reconnect():
                return self.read()
            return False, None

    def isOpened(self):
        """Check if the video stream is opened"""
        return self.cap is not None and self.cap.isOpened()

    def release(self):
        """Release the video stream"""
        if self.cap is not None:
            self.cap.release()
