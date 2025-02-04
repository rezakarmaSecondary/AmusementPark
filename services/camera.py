import cv2
from typing import Optional
import threading

# Thread-safe frame storage
latest_frames = {}
lock = threading.Lock()

def capture_frame_from_stream(stream_url: str) -> Optional[bytes]:
    # Start a thread for the stream if not already running
    if stream_url not in latest_frames:
        thread = threading.Thread(target=_stream_worker, args=(stream_url,), daemon=True)
        thread.start()
    
    # Wait for a frame (simplified; use async queues in production)
    while True:
        with lock:
            if stream_url in latest_frames:
                return latest_frames[stream_url]

def _stream_worker(stream_url: str):
    cap = cv2.VideoCapture(stream_url)
    while True:
        ret, frame = cap.read()
        if ret:
            with lock:
                latest_frames[stream_url] = frame