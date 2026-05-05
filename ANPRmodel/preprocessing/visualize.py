import cv2
import numpy as np

def draw_grid_and_coordinates(frame, grid_spacing=100):
    """Draw coordinate grid on frame"""
    height, width = frame.shape[:2]
    
    # Draw grid lines
    for x in range(0, width, grid_spacing):
        cv2.line(frame, (x, 0), (x, height), (128, 128, 128), 1)
        cv2.putText(frame, str(x), (x, 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    for y in range(0, height, grid_spacing):
        cv2.line(frame, (0, y), (width, y), (128, 128, 128), 1)
        cv2.putText(frame, str(y), (5, y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

def draw_slope_points(frame, slope_inner, slope_middle):
    """Draw slope points with coordinates"""
    # Draw inner slope points
    for point in slope_inner:
        cv2.circle(frame, point, 5, (0, 255, 0), -1)
        coord_text = f"({point[0]}, {point[1]})"
        cv2.putText(frame, coord_text, 
                   (point[0]+10, point[1]-10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # Draw middle slope points
    for point in slope_middle:
        cv2.circle(frame, point, 5, (0, 0, 255), -1)
        coord_text = f"({point[0]}, {point[1]})"
        cv2.putText(frame, coord_text, 
                   (point[0]+10, point[1]-10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

def draw_lane_boundaries(frame, slope_inner, slope_middle):
    """Draw lane boundary lines on the frame for debugging"""
    height, width = frame.shape[:2]
    
    # Draw coordinate grid
    draw_grid_and_coordinates(frame)
    
    # Draw slope points with coordinates
    draw_slope_points(frame, slope_inner, slope_middle)
    
    # Draw inner boundary line
    cv2.line(frame, 
             (slope_inner[0][0], slope_inner[0][1]),
             (slope_inner[1][0], slope_inner[1][1]),
             (0, 255, 0), 2)  # Green line
    
    # Draw middle boundary line
    cv2.line(frame,
             (slope_middle[0][0], slope_middle[0][1]),
             (slope_middle[1][0], slope_middle[1][1]),
             (0, 0, 255), 2)  # Red line
    
    # Add labels with background for better visibility
    labels = [
        ("Inner Lane", (10, 30), (0, 255, 0)),
        ("Middle Lane", (width//2 - 100, 30), (0, 0, 255)),
        ("Outer Lane", (width - 200, 30), (255, 0, 0))
    ]
    
    for text, pos, color in labels:
        # Add black background for text
        (text_width, text_height), _ = cv2.getTextSize(
            text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
        cv2.rectangle(frame, 
                     (pos[0]-5, pos[1]-text_height-5),
                     (pos[0]+text_width+5, pos[1]+5),
                     (0, 0, 0), -1)
        # Add text
        cv2.putText(frame, text, pos, 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    
    return frame

def add_detection_box(frame, x1, y1, x2, y2, lane):
    """Add detection box with lane information"""
    color = {
        "Inner (Lane 1)": (0, 255, 0),
        "Middle (Lane 2)": (0, 0, 255),
        "Outer (Lane 3)": (255, 0, 0)
    }.get(lane, (255, 255, 255))
    
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
    cv2.putText(frame, lane, (x1, y1-10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    return frame
