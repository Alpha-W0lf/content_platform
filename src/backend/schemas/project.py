from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import UUID4, BaseModel


class ProjectStatus(str, Enum):
    CREATED = "CREATED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"


class ProjectBase(BaseModel):
    topic: str
    notes: Optional[str] = None


class ProjectCreate(ProjectBase):
    name: Optional[str] = None


class ProjectRead(ProjectBase):
    id: UUID4
    name: Optional[str] = None  # Name will be set later from script processing
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectStatusResponse(BaseModel):
    status: ProjectStatus


class ProjectUpdate(BaseModel):
    topic: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[ProjectStatus] = None
