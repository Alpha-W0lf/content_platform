from sqlalchemy import Column, String, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=True)  # Name can be null initially
    status = Column(SQLEnum("CREATED", "PROCESSING", "COMPLETED", "ERROR", name="project_status"))
    topic = Column(String, nullable=False)
    notes = Column(String, nullable=True)  # Adding notes field
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Define relationship with proper cascade
    assets = relationship("Asset", back_populates="project", cascade="all, delete-orphan")