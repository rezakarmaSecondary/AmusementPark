from datetime import datetime, date
from pydantic import BaseModel 

class CameraBase(BaseModel):
    name: str
    stream_url: str
    device_id: str

class CameraCreate(CameraBase):
    pass

class CameraResponse(CameraBase):
    id: int
    class Config:
        from_attributes = True  # ORM mode

class BoundingBoxCreate(BaseModel):
    coordinates: dict

class DeviceStartRequest(BaseModel):
    device_id: str  # This was missing

class DeviceLogResponse(BaseModel):
    device_id: str
    start_time: datetime
    persons_detected: int

class ImageDetectionRequest(BaseModel):
    image_url: str
    device_id: str = None  # Optional if using stored bounding box
    coordinates: dict = None  # Optional custom bounding box


    # ... (existing schemas above)

class CameraPurposeCreate(BaseModel):
    camera_id: int
    purpose: str
    device_id: str

class PersonTrackingResponse(BaseModel):
    device_id: str
    tracking_id: int
    entry_time: datetime = None
    exit_time: datetime = None

class DailySummaryResponse(BaseModel):
    device_id: str
    date: date
    total_entries: int
    total_exits: int