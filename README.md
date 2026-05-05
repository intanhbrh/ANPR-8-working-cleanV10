# ANPR-8-working-cleanV8

This is an Automatic Number Plate Recognition project. The purpose is used for dismissal period to inform students of the arrival of their parents. 

## Installation

Install PyTorch with Conda. _(Recommended)_

Install the following packages / libraries into the correct environment either using `pip install` or `conda install` :

* easyocr
* flask
* flask_socketio
* gTTS
* NumPY
* OpenCV (cv2)
* panda
* sqlite3
* Ultralytics
* easyocr

_(Note : There might be missing packages or libraries not mentioned)_


## Run the Project

To run this project, you will need to ensure you are using the correct environment path.

`C:/Users/user/anaconda3/envs/torch/python.exe` **OR** any environment with the required libraries installed.

**TO RUN THE PROGRAM:**
```
Press run
```

**TO END THE PROGRAM:**
```
Close the Terminal / Kill Terminal
```

## Updating the Database

To update the database, you will need to add in your new `.xlsx` in replacement of the old one.

Ensure that you have change the file in [update_db.py](update_db.py) for the following line:  

```python
db.update_database(r'Vehicle Registration 2024_25.xlsx')
```

Then run `update_db.py`, and your database will be updated.


## Current Update

V1: Removed extra file

V2: Cleaned up app.py & database.py 

V3: Added Visualisation and Config

V4: Changed from turboflask to Websocket (Eliminate the need for auto refresh)

V5: Add audio module via Speech Synthesis API

V6: Added Update Database (Clear all record before importing)

V7: Added Auto Reconnection System for Camera (Incase if it disconnect)

V8: Reannounce and update list if lanes are changed & Added Custom Pronunciation (Fine Tuning Required)

V9: Made the website responsive

V10: Added a timer to clear global variable lists to update and clean website

V11: [WORK IN PROGRESS] Experimenting with Super Resolution to enhance the plate for better recognition & Added a brief Logging function

## Things To Fix / Check

* Ensure that Announcer is automatically on if possible 
  * Solution 1: Add the site to allowed to play sound or autoplay
    * Chrome Browser: `chrome://settings/content/sound`
    * Microsoft Edge: `edge://settings/content/mediaAutoplay`
  * Solution 2: Create javascript `<script>` to try and bypass autoplay policy restriction
  * Solution 3: Change from Speech Synthesis API to gTTS. _(Create the audio from backend and push to be played on frontend)_
* Lane Issue with Test Video
* Announcer's pronunciation
  * Solution 1: Add Custom Pronunciation (Manual Labour to Update)
    * Take note of the speed of pronunciation
    * Monitor and Check Pronunciation
  * Solution 2: Use an alternative Text-To-Speech (tts) 
    * responsivevoice
    * Google Cloud Text-to-Speech API
    * Amazon Polly
* Unique Problem to Chrome: 
  * Speech Synthesis API stops working after the first announcement
* Scheduler
  * KIV _(Keep In View)_

## Contributing

HELP International School's students and teachers.

## License

HELP International School
