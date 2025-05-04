import cv2
import redis
import time
import django
import os
import json

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vision_desk_backend.settings")
django.setup()

# Connect to Redis
r = redis.Redis(host="localhost", port=6379, db=5)
cap = cv2.VideoCapture("rtsp://192.168.1.110:8554/mystream")
# cap = cv2.VideoCapture("rtsp://admin:HomeCamera2025@192.168.0.200:554/Streaming/Channels/101/?transportmode=unicast&streamtype=main")
# cap = cv2.VideoCapture("http://192.168.1.112:8001/video")
RED_ORANGE_GREEN = [
    (0, 0, 255),  # Red -> away from table
    (0, 255, 0),  # Green -> working
    (0, 165, 255),  # Orange -> idle
]


def annotate_frame(frame):
    # get the latest bounding boxes from Redis
    latest_bounding_boxes = r.get("latest_bounding_boxes")
    print("latest_bounding_boxes", latest_bounding_boxes)

    if latest_bounding_boxes is None:
        return frame

    # Decode the JSON data
    bounding_boxes = json.loads(latest_bounding_boxes.decode("utf-8"))

    ## draw person bounding boxes
    """
    format:
    person_bound_boxes": {
        "0": [
            120,
            180,
            200,
            260
        ],
    """
    for box in bounding_boxes["person_bound_boxes"]:
        x1, y1, x2, y2 = bounding_boxes["person_bound_boxes"][box]
        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            RED_ORANGE_GREEN[bounding_boxes["person_status"][box]],
            1,
        )

    # Write texts on the frame
    cv2.putText(
        frame,
        f"Total Person: {bounding_boxes["n_person"]}",
        (10, 15),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.35,
        (0, 255, 0),
        1,
    )
    cv2.putText(
        frame,
        f"Total Table: {bounding_boxes["n_tables"]}",
        (10, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.35,
        (0, 255, 0),
        1,
    )
    cv2.putText(
        frame,
        f"Working: {bounding_boxes["person_in_the_table"]}",
        (10, 55),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.35,
        (0, 255, 0),
        1,
    )
    cv2.putText(
        frame,
        f"Idle: {bounding_boxes["person_idle"]}",
        (10, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.35,
        (0, 255, 0),
        1,
    )
    cv2.putText(
        frame,
        f"Away from table: {bounding_boxes["person_away"]}",
        (10, 95),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.35,
        (0, 255, 0),
        1,
    )

    # Dummy ML processing (convert to grayscale as an example)
    return frame


while True:
    success, frame = cap.read()
    if not success:
        time.sleep(0.5)
        continue

    annotated_frame = annotate_frame(frame)

    # Store annotated frame to Redis
    _, jpeg = cv2.imencode(".jpg", annotated_frame)
    r.set("latest_frame", jpeg.tobytes())
