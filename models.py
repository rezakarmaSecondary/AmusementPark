from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Date  
from sqlalchemy.orm import relationship
from datetime import datetime, date  
from database import Base

class Camera(Base):
    __tablename__ = "cameras"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)
    stream_url = Column(String(512))
    device_id = Column(String(255))
    bounding_boxes = relationship("BoundingBox", back_populates="camera")
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "stream_url": self.stream_url,
            "device_id": self.device_id
        }

class BoundingBox(Base):
    __tablename__ = "bounding_boxes"
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"))
    coordinates = Column(JSON)  # {"x1": 0.2, "y1": 0.3, "x2": 0.8, "y2": 0.7}
    valid_from = Column(DateTime, default=datetime.utcnow)
    camera = relationship("Camera", back_populates="bounding_boxes")
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "stream_url": self.stream_url,
            "device_id": self.device_id
        }
    
class DeviceLog(Base):
    __tablename__ = "device_logs"
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(255))
    start_time = Column(DateTime, default=datetime.utcnow)
    persons_detected = Column(Integer)
    image_path = Column(String(512))
    
__all__ = ["Camera", "BoundingBox", "DeviceLog"]


# ... (existing models above)

class CameraPurpose(Base):
    __tablename__ = "camera_purposes"
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"))
    purpose = Column(String(50))  # 'entry' or 'exit'
    device_id = Column(String(255))

class PersonTracking(Base):
    __tablename__ = "person_tracking"
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(255))
    tracking_id = Column(Integer)  # From DeepSORT
    entry_time = Column(DateTime)
    exit_time = Column(DateTime)
    last_seen = Column(DateTime)
    cooldown_until = Column(DateTime)

class DailySummary(Base):
    __tablename__ = "daily_summaries"
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(255))
    date = Column(Date)
    total_entries = Column(Integer, default=0)
    total_exits = Column(Integer, default=0)