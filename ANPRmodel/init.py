import cv2
from ultralytics import YOLO
from ANPRmodel.database.database import SQL_database
from ANPRmodel.errors.errors import AakashError
from ANPRmodel.video_stream import VideoStream

def initalise(plate_model_path, video_feed_1, db_path):
    try:
        plate_model = YOLO(plate_model_path)
        # Use the new VideoStream class instead of cv2.VideoCapture
        cap_1 = VideoStream(video_feed_1, retry_interval=3, max_retries=None)
        
        database = SQL_database(db_path)
        sqliteConnection, cursor = database.create_connection()

        return plate_model, cap_1, database, sqliteConnection, cursor
    
    except Exception as error:
        raise AakashError(error)