from gtts import gTTS
import os
import threading
from pathlib import Path
from queue import Queue
import time

class AudioManager:
    def __init__(self):
        self.audio_folder = Path("static")
        self.audio_folder.mkdir(parents=True, exist_ok=True)
        self.audio_queue = Queue()
        self.processing_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.processing_thread.start()
        self._cleanup_old_files()

    def _cleanup_old_files(self):
        """Remove old audio files to prevent disk space issues"""
        try:
            for file in self.audio_folder.glob("*.mp3"):
                file.unlink()
        except Exception as e:
            print(f"Error cleaning up audio files: {e}")

    def _process_queue(self):
        """Process audio generation requests from queue"""
        while True:
            try:
                data, filepath = self.audio_queue.get()
                if data is None:
                    continue

                students = [name.strip() for name in data[0][:4] if name.strip()]
                year_groups = [year.strip() for year in data[0][4:8] if year.strip()]
                lane = data[0][-1]

                # Create announcement text with student names and year groups
                student_year_pairs = []
                for student, year in zip(students, year_groups):
                    student_year_pairs.append(f"{student}, {year}")
                
                text = f"{', '.join(student_year_pairs)}, {lane}"

                print(f"Generating audio file at: {filepath}")
                # Generate audio
                tts = gTTS(text=text, lang='en')
                tts.save(filepath)
                print(f"Successfully saved audio file to: {filepath}")

                self.audio_queue.task_done()

            except Exception as e:
                print(f"Error processing audio queue: {e}")
                time.sleep(0.1)  # Prevent busy-waiting on errors

    def generate_audio(self, data):
        """
        Queue audio generation request
        """
        if not data:
            print("No data provided for audio generation")
            return None

        try:
            print(f"Generating audio for data: {data}")  # Debug
            
            # Generate expected filename
            students = [name.strip() for name in data[0][:4] if name.strip()]
            year_groups = [year.strip() for year in data[0][4:8] if year.strip()]
            lane = data[0][-1]
            
            student_year_pairs = []
            for student, year in zip(students, year_groups):
                student_year_pairs.append(f"{student}, {year}")
            
            text = f"{', '.join(student_year_pairs)}, {lane}"
            filename = f"announcement_{abs(hash(text))}.mp3"  # Use absolute value of hash
            
            # Fix path handling - audio files go directly in static/audio
            filepath = self.audio_folder / "audio" / filename
            
            # Ensure audio subdirectory exists
            (self.audio_folder / "audio").mkdir(exist_ok=True)
            
            # Add to queue for processing
            self.audio_queue.put((data, str(filepath)))
            
            print(f"Generated filepath: {filepath}")  # Debug
            # Return correct relative path
            return f"audio/{filename}"  # Simplified path structure

        except Exception as e:
            print(f"Error queueing audio generation: {e}")
            return None