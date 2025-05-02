import cv2
import redis
import time
import django
import os

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vision_desk_backend.settings")
django.setup()

from administrator.buffer import StatusBuffer
status_buffer = StatusBuffer()

# Connect to Redis
r = redis.Redis(host="localhost", port=6379, db=5)

cap = cv2.VideoCapture("http://127.0.0.1:8001/video")


import random
def process_frame(frame):
    
    # Dummy ML processing (convert to grayscale as an example)
    return {
        "frame": cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY),
        # "frame": frame,
        "desk_no": 1,
        # "status_enum": random.choice([0, 1, 2]),  # Random status for demonstration
        "status_enum": 1
    }


while True:
    success, frame = cap.read()
    if not success:
        time.sleep(0.5)
        continue

    detection_dict = process_frame(frame)

    # Add status to buffer
    status_buffer.add_status(
        desk_no=detection_dict["desk_no"],
        status_enum=detection_dict["status_enum"],
    )

    # Store annotated frame to Redis
    _, jpeg = cv2.imencode(".jpg", detection_dict["frame"])
    r.set("latest_frame", jpeg.tobytes())

    # time.sleep(0.1)  # Add slight delay to control FPS
