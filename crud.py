from sqlalchemy.orm import Session
from models import Camera, BoundingBox, DeviceLog, CameraPurpose, PersonTracking
from datetime import datetime, timedelta
from schemas import CameraPurposeCreate
# --- Camera Operations ---
def get_camera_by_id(db: Session, camera_id: int):
    return db.query(Camera).filter(Camera.id == camera_id).first()

def get_camera_by_device_id(db: Session, device_id: str):
    return db.query(Camera).filter(Camera.device_id == device_id).first()

# crud.py (example for create_camera)
def create_camera(db: Session, name: str, stream_url: str, device_id: str):
    camera = Camera(name=name, stream_url=stream_url, device_id=device_id)
    db.add(camera)
    db.commit()
    db.refresh(camera)
    return camera  # Convert to dict for Pydantic

# --- Bounding Box Operations ---
def create_bounding_box(db: Session, camera_id: int, coordinates: dict):
    bbox = BoundingBox(camera_id=camera_id, coordinates=coordinates)
    db.add(bbox)
    db.commit()
    db.refresh(bbox)
    return bbox

def get_latest_bounding_box(db: Session, camera_id: int):
    return (
        db.query(BoundingBox)
        .filter(BoundingBox.camera_id == camera_id)
        .order_by(BoundingBox.valid_from.desc())
        .first()
    )

# --- Device Log Operations ---
def create_device_log(db: Session, device_id: str, persons_detected: int, image_path: str):
    log = DeviceLog(
        device_id=device_id,
        persons_detected=persons_detected,
        image_path=image_path
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


# ... (existing CRUD above)

def create_camera_purpose(db: Session, camera_purpose: CameraPurposeCreate):
    db_purpose = CameraPurpose(**camera_purpose.dict())
    db.add(db_purpose)
    db.commit()
    db.refresh(db_purpose)
    return db_purpose

def get_camera_purpose(db: Session, camera_id: int):
    return db.query(CameraPurpose).filter(CameraPurpose.camera_id == camera_id).first()

def create_person_tracking(db: Session, device_id: str, tracking_id: int, is_entry: bool):
    now = datetime.utcnow()
    entry_time = now if is_entry else None
    exit_time = now if not is_entry else None
    tracking = PersonTracking(
        device_id=device_id,
        tracking_id=tracking_id,
        entry_time=entry_time,
        exit_time=exit_time,
        last_seen=now,
        cooldown_until=now + timedelta(minutes=3)
    )
    db.add(tracking)
    db.commit()
    return tracking

def get_recent_tracking(db: Session, device_id: str, tracking_id: int):
    return db.query(PersonTracking).filter(
        PersonTracking.device_id == device_id,
        PersonTracking.tracking_id == tracking_id,
        PersonTracking.cooldown_until > datetime.utcnow()
    ).first()