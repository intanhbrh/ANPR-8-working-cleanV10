"""
Automatic Number Plate Recognition (ANPR) prediction module.
Handles license plate detection, text extraction, and database validation.
"""

from ANPRmodel.detect_lane import detect_lane
from ANPRmodel.read.read_easy import read_text
from ANPRmodel.preprocessing.visualize import draw_lane_boundaries, add_detection_box
import cv2
from config import show_visualization, LIVE_FEED, LIVE_SLOPES, TEST_SLOPES
import time

def predict(model, cap, database, cursor):
    """
    Process video frame to detect and validate license plates.
    
    Args:
        model: YOLOv8 model for plate detection
        cap: Video capture object
        database: Database interface object
        cursor: Database cursor
    
    Returns:
        tuple: Validated plate information with lane detection or None
    """
    try:
        if not cap.isOpened():
            print("Error: Video capture device is not open")
            return None
            
        # Select appropriate slopes based on feed type
        slopes = LIVE_SLOPES if LIVE_FEED else TEST_SLOPES
        slope_inner = slopes['inner']
        slope_middle = slopes['middle']

        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to read frame")
            return None

        # Get frame timestamp for FPS control
        frame_time = time.time()
        output_data = None

        try:
            # Draw visualization before detection
            if show_visualization:
                draw_lane_boundaries(frame, slope_inner, slope_middle)

            # Process frame with YOLOv8
            results = model(frame, stream=True, verbose=False)
            
            # Convert results iterator to list to check if empty
            results_list = list(results)
            if not results_list:
                if show_visualization:
                    cv2.imshow('Source Feed', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        cv2.destroyAllWindows()
                return None

            # Process first result (should only be one)
            r = results_list[0]
            if not r.boxes:
                if show_visualization:
                    cv2.imshow('Source Feed', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        cv2.destroyAllWindows()
                return None

            # Process detections
            for box in r.boxes:
                if box.cls == 1:  # License plate detection
                    try:
                        x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                        
                        # Get lane info first for visualization
                        lane = detect_lane(x1, y1, x2, y2, slope_inner, slope_middle)
                        
                        # Draw detection box if visualization enabled
                        if show_visualization:
                            add_detection_box(frame, x1, y1, x2, y2, lane)
                        
                        # Process plate text
                        text = read_text(frame, x1, y1, x2, y2)
                        if not text or not text[0]:
                            continue
                            
                        formatted_plate = database.format_plate(str(text[0][-1]))
                        if not formatted_plate:
                            continue

                        # Database lookup
                        combinations = database.plate_combinations(formatted_plate)
                        for combination in combinations:
                            output, success = database.find_plate(cursor, combination)
                            if success:
                                list_output = list(output[0])
                                list_output.append(lane)
                                output_data = [tuple(list_output)]
                                break
                    except (IndexError, AttributeError) as e:
                        print(f"Detection processing error: {e}")
                        continue

            # Show visualization window if enabled
            if show_visualization:
                elapsed = time.time() - frame_time
                delay = max(1, int(33 - elapsed * 1000))
                cv2.imshow('Source Feed', frame)
                if cv2.waitKey(delay) & 0xFF == ord('q'):
                    cv2.destroyAllWindows()

            return output_data

        except Exception as e:
            print(f"Error in plate processing: {e}")
            return None

    except cv2.error as e:
        print(f"OpenCV error: {e}")
        return None
    except Exception as e:
        print(f"Prediction error: {e}")
        return None