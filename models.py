from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Camera(Base):
    __tablename__ = "cameras"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)
    stream_url = Column(String(512))
    device_id = Column(String(255))
    bounding_boxes = relationship("BoundingBox", back_populates="camera")

class BoundingBox(Base):
    __tablename__ = "bounding_boxes"
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"))
    coordinates = Column(JSON)  # {"x1": 0.2, "y1": 0.3, "x2": 0.8, "y2": 0.7}
    valid_from = Column(DateTime, default=datetime.utcnow)
    camera = relationship("Camera", back_populates="bounding_boxes")

class DeviceLog(Base):
    __tablename__ = "device_logs"
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(255))
    start_time = Column(DateTime, default=datetime.utcnow)
    persons_detected = Column(Integer)
    image_path = Column(String(512))