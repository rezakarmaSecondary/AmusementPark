from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://neondb_owner:npg_IzltSL14EwuR@ep-empty-bar-a8i23a4z-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"



# Synchronous engine (simpler for beginners)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

from models import Camera, BoundingBox, DeviceLog 

Base.metadata.create_all(bind=engine)
# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 