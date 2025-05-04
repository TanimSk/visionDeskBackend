import cv2
import time
from datetime import datetime

# ==== Configuration ====
rtsp_url = "rtsp://192.168.1.110:8554/mystream"  # Update as needed
frame_sample_rate = 1  # Save every Nth frame
record_key = ord('r')
quit_key = ord('q')

# ==== Custom save resolution (set to None to use original) ====
save_width = 640 # None
save_height = 360 # None

# ==== Setup ====
cap = cv2.VideoCapture(rtsp_url)
if not cap.isOpened():
    print("Failed to connect to RTSP stream.")
    exit()

fps = cap.get(cv2.CAP_PROP_FPS) or 25
input_width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
input_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = None
recording = False
frame_count = 0

print("Press 'r' to start/stop recording, 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Frame not received. Retrying...")
        time.sleep(0.5)
        continue

    frame_count += 1

    # ==== Save frame to file ====
    if recording and frame_count % frame_sample_rate == 0:
        if out is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recorded_{timestamp}.mp4"
            if save_width and save_height:
                out = cv2.VideoWriter(filename, fourcc, fps // frame_sample_rate, (save_width, save_height))
            else:
                out = cv2.VideoWriter(filename, fourcc, fps // frame_sample_rate, (input_width, input_height))
            print(f"Started recording: {filename}")

        # Resize if save resolution is set
        if save_width and save_height:
            frame_to_save = cv2.resize(frame, (save_width, save_height))
        else:
            frame_to_save = frame

        out.write(frame_to_save)

    # ==== Prepare frame for display ====
    frame_display = frame.copy()

    # ==== Draw indicator on preview ====
    indicator_radius = 10
    margin = 20
    center = (input_width - margin, margin)

    if recording:
        cv2.circle(frame_display, center, indicator_radius, (0, 255, 0), -1)  # Green circle
    else:
        cv2.rectangle(frame_display,
                      (input_width - margin - indicator_radius, margin - indicator_radius),
                      (input_width - margin + indicator_radius, margin + indicator_radius),
                      (0, 0, 255), -1)  # Red square

    # ==== Show preview ====
    cv2.imshow("RTSP Stream", frame_display)

    key = cv2.waitKey(1) & 0xFF

    if key == record_key:
        recording = not recording
        if not recording:
            print("Stopped recording.")
            if out:
                out.release()
                out = None

    elif key == quit_key:
        print("Exiting.")
        break

# ==== Cleanup ====
cap.release()
if out:
    out.release()
cv2.destroyAllWindows()

