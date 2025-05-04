import subprocess
import time
import os

def stream_video_loop(video_path, rtsp_url):
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")

    ffmpeg_cmd = [
        "ffmpeg",
        "-stream_loop", "-1",             # Loop infinitely
        "-re",                            # Read input at native frame rate
        "-i", video_path,
        "-vcodec", "copy",
        "-f", "rtsp",
        rtsp_url
    ]

    try:
        print("Starting RTSP stream...")
        subprocess.run(ffmpeg_cmd)
    except KeyboardInterrupt:
        print("Stream interrupted.")

if __name__ == "__main__":
    video_file = "./sample.mp4"  # Replace with your video file
    rtsp_url = "rtsp://localhost:8554/mystream"
    stream_video_loop(video_file, rtsp_url)