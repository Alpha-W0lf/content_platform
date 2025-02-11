from pydantic import BaseModel, UUID4
from typing import Optional
from datetime import datetime

class ProjectBase(BaseModel):
    topic: str
    notes: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectStatus(BaseModel):
    status: str

class Project(ProjectBase):
    id: UUID4
    name: Optional[str] = None  # Name will be set later from script processing
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True