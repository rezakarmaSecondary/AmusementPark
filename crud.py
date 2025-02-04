from sqlalchemy.orm import Session
from models import Camera, BoundingBox, DeviceLog

# --- Camera Operations ---
def get_camera_by_id(db: Session, camera_id: int):
    return db.query(Camera).filter(Camera.id == camera_id).first()

def get_camera_by_device_id(db: Session, device_id: str):
    return db.query(Camera).filter(Camera.device_id == device_id).first()

def create_camera(db: Session, name: str, stream_url: str, device_id: str):
    camera = Camera(name=name, stream_url=stream_url, device_id=device_id)
    db.add(camera)
    db.commit()
    db.refresh(camera)
    return camera

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