import threading
import time
from datetime import datetime, timedelta
import cv2
from database import SessionLocal
from models import CameraPurpose, PersonTracking
from crud import get_recent_tracking, create_person_tracking

def tracking_worker(stream_url: str, purpose: str, device_id: str):
    db = SessionLocal()
    try:
        cap = cv2.VideoCapture(stream_url)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Get camera's bounding box from database
            camera = get_camera_by_stream_url(db, stream_url)
            if not camera:
                continue
            bbox = get_latest_bounding_box(db, camera.id)
            if not bbox:
                continue

            tracks = detect_and_track(frame, bbox.coordinates)
            
            for track in tracks:
                if not track.is_confirmed():
                    continue
                
                track_id = track.track_id
                existing = get_recent_tracking(db, device_id, track_id)
                
                if not existing:
                    create_person_tracking(
                        db,
                        device_id=device_id,
                        tracking_id=track_id,
                        is_entry=(purpose == "entry")
                    )
            
            time.sleep(0.1)  # Reduce CPU usage
    finally:
        db.close()