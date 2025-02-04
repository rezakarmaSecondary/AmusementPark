# schemas.py
from pydantic import BaseModel
from datetime import datetime

class CameraBase(BaseModel):
    name: str
    stream_url: str
    device_id: str

class CameraCreate(CameraBase):
    pass

class CameraResponse(CameraBase):
    id: int
    class Config:
        from_attributes = True  # Allows ORM mode

class BoundingBoxCreate(BaseModel):
    coordinates: dict

class DeviceLogResponse(BaseModel):
    device_id: str
    start_time: datetime
    persons_detected: int