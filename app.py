from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import threading
import os
import logging
import time
import queue
from config import LIVE_FEED
from ANPRmodel.predict import predict
from ANPRmodel.init import initalise
from ANPRmodel.testing.diagnostics import model_test
from flask_cors import CORS

# Configuration
MODEL_PATH = os.path.join("ANPRmodel", "train", "runs", "detect", "train34", "weights", "best.pt")
CAMERA_URL = "rtsp://admin:admin123@10.250.10.220:554/cam/realmonitor?channel=1&subtype=0" if LIVE_FEED else os.path.join('ANPRmodel', 'testing', 'test_data', 'test_vid.mp4')
DATABASE_PATH = os.path.join("ANPRmodel", "database", "database.db")
HOST = '10.250.34.10' # Change to your own local host IP
PORT = 80

# Suppress excessive logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Increase queue size and add last processed time tracking
message_queue = queue.Queue(maxsize=100)
last_processed_time = 0
MIN_UPDATE_INTERVAL = 0.016  # About 60fps

class CurrentState:
    def __init__(self):
        self.current_students = ""
        self.current_lane = ""
        self.recent_list = "<ol></ol>"
        # Add lane tracking dictionary
        self.student_lanes = {}  # Format: {student_name: last_known_lane}

state = CurrentState()

# Add inactivity timer and clearing functionality
last_activity_time = time.time()
INACTIVITY_TIMEOUT = 180  # 3 minutes in seconds

def reset_activity_timer():
    global last_activity_time
    last_activity_time = time.time()

def clear_global_variables():
    global global_output, recentlist, PREVOUTPUT, RECENTCARS, siblings, state
    global_output = None
    recentlist = ""
    PREVOUTPUT = []
    RECENTCARS = []
    siblings = []
    state.current_students = ""
    state.current_lane = ""
    state.recent_list = "<ol></ol>"
    state.student_lanes = {}

def check_inactivity():
    while True:
        try:
            current_time = time.time()
            if current_time - last_activity_time > INACTIVITY_TIMEOUT:
                clear_global_variables()
                try:
                    message_queue.put_nowait({
                        'studentname': "",
                        'lane': "",
                        'recent_list': "<ol></ol>"
                    })
                except queue.Full:
                    pass
            time.sleep(10)  # Check every 10 seconds
        except Exception as e:
            print(f"Error in check_inactivity: {e}")

def check_model(test=False):
    try:
        test_path = os.path.join('ANPRmodel', 'testing', 'test_data', 'test_vid.mp4')
        model_path = os.path.join('ANPRmodel', 'train', 'runs', 'detect', 'train12', 'weights', 'best.pt')
        video_source = test_path if test else CAMERA_URL
        
        # Add connection retry logic
        retry_count = 3
        while retry_count > 0:
            try:
                model_test(model_path, video_source)
                break
            except Exception as e:
                print(f"Model test attempt failed: {e}")
                retry_count -= 1
                time.sleep(2)
                
        if retry_count == 0:
            print("Failed to initialize video stream after 3 attempts")
            
    except Exception as e:
        print(f"Error in check_model: {e}")

# Initialize Flask and SocketIO with debug mode
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, 
                   cors_allowed_origins="*", 
                   transport=["websocket"],
                   logger=True, 
                   engineio_logger=True,
                   async_mode='threading',
                   ping_timeout=35,  # Increased timeout
                   ping_interval=25)  # More frequent pings

# Initialize the ANPR model and database
plate_model, cap_1, database, sqliteConnection, cursor = initalise(
    MODEL_PATH, CAMERA_URL, DATABASE_PATH
)

# Global variables
global_output = None
recentlist = ""
PREVOUTPUT = []
RECENTCARS = []
siblings = []

def update_load():
    global recentlist, global_output, RECENTCARS, last_processed_time, state
   
    while True:
        try:
            output = predict(plate_model, cap_1, database, cursor)
            current_time = time.time()
           
            if current_time - last_processed_time < MIN_UPDATE_INTERVAL or not output:
                continue
           
            # Reset activity timer when new data is detected
            reset_activity_timer()
           
            current_siblings = []
            lane_changed = False
            detected_lane = output[0][8]

            # Process siblings and check for lane changes
            for i in range(4):
                name = output[0][i].strip()
                year = output[0][i+4].strip()
               
                if name and year and name != "-n/a-" and year != " " and year != "-n/a-":
                    student_id = f'{name} ({year})'
                    current_siblings.append(student_id)
                   
                    # Check if student's lane has changed
                    if student_id in state.student_lanes:
                        if state.student_lanes[student_id] != detected_lane:
                            lane_changed = True
                    state.student_lanes[student_id] = detected_lane

            siblings_str = ", ".join(current_siblings)
           
            # Create the complete string for the recent list entry, including the lane.
            full_display_str = f'{siblings_str} - {detected_lane}'
           
            # Update display if it's a new detection or lane has changed
            # We check the full string (students + lane) against the RECENTCARS list.
            if siblings_str and full_display_str not in RECENTCARS:
               
                # We skip the check for 'lane_changed' here because checking
                # 'full_display_str not in RECENTCARS' already handles the case
                # where a car moves to a new lane (e.g., "Car A - Lane 1" != "Car A - Lane 2").
               
                # ADD THE COMPLETE STRING (students + lane) to the history list
                RECENTCARS.append(full_display_str)
               
                if len(RECENTCARS) > 10:
                    RECENTCARS.pop(0)
                   
                # Rebuild the HTML list using the complete strings from RECENTCARS.
                recentlist = "<ol><li>" + "</li><li>".join(RECENTCARS[::-1]) + "</li></ol>"
               
                # Update current state
                state.current_students = siblings_str
                state.current_lane = detected_lane
                state.recent_list = recentlist
               
                try:
                    message_queue.put_nowait({
                        'studentname': siblings_str,
                        'lane': detected_lane,
                        'recent_list': recentlist
                    })
                    last_processed_time = current_time
                except queue.Full:
                    continue
                   
        except Exception as e:
            print(f"Error in update_load: {e}")

def emit_updates():
    """Handle WebSocket emissions in a separate thread"""
    retry_delay = 0.001
    max_delay = 1.0
    
    while True:
        try:
            data = message_queue.get_nowait()
            with app.app_context():
                try:
                    socketio.emit('update_data', data, namespace='/')
                    retry_delay = 0.001  # Reset delay on successful emission
                except Exception as e:
                    print(f"Socket emission error: {e}")
                    retry_delay = min(retry_delay * 2, max_delay)
        except queue.Empty:
            time.sleep(retry_delay)
        except Exception as e:
            print(f"Error in emit_updates: {e}")
            time.sleep(retry_delay)

@socketio.on('ping')
def handle_ping():
    emit('pong')

@socketio.on('connect')
def handle_connect():
    try:
        print(f"Client connected", flush=True)
        
        # Send current state immediately
        emit('update_data', {
            'studentname': state.current_students,
            'lane': state.current_lane,
            'recent_list': state.recent_list
        })
    except Exception as e:
        print(f"Error in connect handler: {e}")

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected - SID: {request.sid}", flush=True)

@app.route("/")
def index():
    return render_template("home.html",
                         studentname="",
                         lane="",
                         recent_list="<ol></ol>")

@app.route("/data", methods=['GET'])
def data():
    print(f"Current global output: {global_output}")
    try:
        return jsonify({
            'student_name_1': global_output[0][0],
            'student_name_2': global_output[0][1],
            'student_name_3': global_output[0][2],
            'student_name_4': global_output[0][3],
            'student_year_1': global_output[0][5],
            'student_year_2': global_output[0][6],
            'student_year_3': global_output[0][7],
            'student_year_4': global_output[0][8],
            'lane': global_output[0][9]
        })
    except TypeError:
        return jsonify({
            'student_name_1': None,
            'student_name_2': None,
            'student_name_3': None,
            'student_name_4': None,
            'student_year_1': None,
            'student_year_2': None,
            'student_year_3': None,
            'student_year_4': None,
            'lane': None
        })

def start_application():
    try:
        # Initialize threads with error handling
        threads = []
        
        for thread_target in [update_load, emit_updates, check_model, check_inactivity]:
            thread = threading.Thread(target=thread_target, daemon=True)
            thread.start()
            threads.append(thread)
            
        # Start SocketIO server with correct parameters
        socketio.run(app, 
                    host=HOST, 
                    port=PORT, 
                    debug=True, 
                    use_reloader=False,
                    allow_unsafe_werkzeug=True,
                    log_output=True)
                    
    except Exception as e:
        print(f"Application start error: {e}")
        # Attempt graceful shutdown
        for thread in threads:
            thread.join(timeout=1.0)

if __name__ == '__main__':
    start_application()