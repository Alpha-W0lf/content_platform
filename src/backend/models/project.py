import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.backend.schemas.project import ProjectStatus

from .asset import Asset
from .base import Base


class Project(Base):
    __tablename__ = "projects"

    # Required fields without defaults
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    topic: Mapped[str] = mapped_column(String, nullable=False)

    # Required fields with defaults
    status: Mapped[ProjectStatus] = mapped_column(
        SQLEnum(ProjectStatus), nullable=False, default=ProjectStatus.CREATED
    )

    # Optional fields
    name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Timestamp fields with defaults
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    assets: Mapped[List["Asset"]] = relationship(
        "Asset", back_populates="project", cascade="all, delete-orphan", lazy="selectin"
    )
