from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware  # <-- Add this line
import requests
import numpy as np
from pydantic import BaseModel 
from database import get_db
from models import Camera, BoundingBox  # SQLAlchemy models
from schemas import (                    
    CameraCreate,
    CameraResponse,
    BoundingBoxCreate,
    DeviceStartRequest,
    ImageDetectionRequest  
)
from crud import create_camera, get_camera_by_device_id, create_bounding_box, get_latest_bounding_box, create_device_log
from services.camera import capture_frame_from_stream
from services.detection import detect_persons_in_frame
import uuid
import cv2
from datetime import datetime, timedelta, date
from contextlib import asynccontextmanager
import threading
from database import SessionLocal
from models import CameraPurpose
from services.tracker import tracking_worker
from models import PersonTracking,DailySummary
from schemas import DailySummaryResponse
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start tracking threads on startup
    db = SessionLocal()
    cameras = db.query(CameraPurpose).all()
    for cam in cameras:
        camera = get_camera_by_id(db, cam.camera_id)
        thread = threading.Thread(
            target=tracking_worker,
            args=(camera.stream_url, cam.purpose, cam.device_id),
            daemon=True
        )
        thread.start()
    db.close()
    yield

app = FastAPI(lifespan=lifespan)


from apscheduler.schedulers.background import BackgroundScheduler

@app.on_event("startup")
def init_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(aggregate_daily_summaries, 'cron', hour=0)
    scheduler.start()

def aggregate_daily_summaries():
    db = SessionLocal()
    try:
        yesterday = datetime.utcnow() - timedelta(days=1)
        start = yesterday.replace(hour=0, minute=0, second=0)
        end = start + timedelta(days=1)
        
        devices = db.query(PersonTracking.device_id).distinct().all()
        for device_id in devices:
            entries = db.query(PersonTracking).filter(
                PersonTracking.device_id == device_id[0],
                PersonTracking.entry_time.between(start, end)
            ).count()
            exits = db.query(PersonTracking).filter(
                PersonTracking.device_id == device_id[0],
                PersonTracking.exit_time.between(start, end)
            ).count()
            
            summary = DailySummary(
                device_id=device_id[0],
                date=start.date(),
                total_entries=entries,
                total_exits=exits
            )
            db.add(summary)
            db.commit()
    finally:
        db.close()


# app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Schemas (schemas.py) ---
class CameraCreate(BaseModel):
    name: str
    stream_url: str
    device_id: str

class BoundingBoxCreate(BaseModel):
    coordinates: dict

class DeviceStartRequest(BaseModel):
    device_id: str

# --- API Endpoints ---
@app.post("/cameras/", response_model=CameraResponse)  # Changed from Camera
def add_camera(camera: CameraCreate, db: Session = Depends(get_db)):
    db_camera = create_camera(db, camera.name, camera.stream_url, camera.device_id)
    return db_camera

@app.post("/cameras/{camera_id}/bounding-box")
def add_bounding_box(
    camera_id: int, 
    bbox: BoundingBoxCreate, 
    db: Session = Depends(get_db)
):
    return create_bounding_box(db, camera_id, bbox.coordinates)

@app.post("/device-start")
async def handle_device_start(
    request: DeviceStartRequest, 
    db: Session = Depends(get_db)
):
    # 1. Find camera by device_id
    camera = get_camera_by_device_id(db, request.device_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    # 2. Capture frame from camera stream
    frame = await capture_frame_from_stream(camera.stream_url)

    # 3. Get latest bounding box
    bbox = get_latest_bounding_box(db, camera.id)
    if not bbox:
        raise HTTPException(status_code=400, detail="Bounding box not set")

    # 4. Detect persons in the bounding box
    persons_count = detect_persons_in_frame(frame, bbox.coordinates)

    # 5. Save image and log
    image_path = f"storage/{request.device_id}_{uuid.uuid4()}.jpg"
    cv2.imwrite(image_path, frame)

    create_device_log(db, request.device_id, persons_count, image_path)

    return {"persons_detected": persons_count}



@app.post("/detect-image/")
async def detect_in_image(request: ImageDetectionRequest, db: Session = Depends(get_db)):
    try:
        # Download image
        response = requests.get(request.image_url, timeout=10)
        response.raise_for_status()
        
        # Convert to OpenCV format
        image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        
        # Get bounding box
        if request.coordinates:
            bbox_coords = request.coordinates
        elif request.device_id:
            camera = get_camera_by_device_id(db, request.device_id)
            if not camera:
                raise HTTPException(status_code=404, detail="Camera not found")
            bbox = get_latest_bounding_box(db, camera.id)
            if not bbox:
                raise HTTPException(status_code=400, detail="Bounding box not set")
            bbox_coords = bbox.coordinates
        else:
            raise HTTPException(status_code=400, detail="Provide either device_id or coordinates")
        
        # Detect persons
        persons_count = detect_persons_in_frame(frame, bbox_coords)
        
        return {
            "persons_detected": persons_count,
            "image_size": f"{frame.shape[1]}x{frame.shape[0]}",
            "bounding_box_used": bbox_coords
        }
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Image download failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/daily-summary/{device_id}", response_model=DailySummaryResponse)
def get_daily_summary(device_id: str, date: date, db: Session = Depends(get_db)):
    summary = db.query(DailySummary).filter(
        DailySummary.device_id == device_id,
        DailySummary.date == date
    ).first()
    return summary