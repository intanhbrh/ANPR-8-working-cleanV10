import cv2
from PIL import Image
import os
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator

from easyocr import Reader
reader = Reader(['en'], gpu = True)

from ANPRmodel.errors.errors import VideoStreamError

def model_test(model_path, video_feed, device='0'):
    model = YOLO(model_path)
    cap = cv2.VideoCapture(video_feed)

    while True:
        ret, frame = cap.read()

        if not ret:
            raise VideoStreamError

        results = model(frame, device=device, verbose=False)

        for r in results:
            
            annotator = Annotator(frame)
            boxes = r.boxes
            for box in boxes:
                
                b = box.xyxy[0]
                c = box.cls
                annotator.box_label(b, model.names[int(c)])
            
        frame = annotator.result()  
        cv2.imshow('YOLO V8 Detection', frame) 
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

def test_video_stream(video_feed):
    cap = cv2.VideoCapture(video_feed)

    while True:
        ret, frame = cap.read()

        if not ret:
            raise VideoStreamError

        cv2.imshow('YOLO Object Detection', frame)

        # Exit the loop when 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

def test_YOLO(model_path, image_path, save_path=os.path.join('results', 'output.png')):
    model =  YOLO(model_path)
    results = model(image_path)
    for r in results:
        im_array = r.plot()  # plot a BGR numpy array of predictions
        im = Image.fromarray(im_array[..., ::-1])  # RGB PIL image
        im.save(save_path)
        im.show()  # show image
    return results

def test_OCR(image):
    return reader.readtext(image)

def test_db(database, cursor, plate):
    output, success =  database.find_plate(cursor, plate)
    if success:
        return output
    else:
        return 'Not found in database'
