import uuid
from datetime import datetime, timezone
from typing import Literal
from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped

from .base import Base


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[UUID] = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    asset_type: Mapped[Literal["script", "narration", "video", "image", "slide"]] = Column(
        SQLEnum("script", "narration", "video", "image", "slide", name="asset_type")
    )
    path: Mapped[str] = Column(String, nullable=False)
    approved: Mapped[bool] = Column(Boolean, default=False)
    created_at: Mapped[datetime] = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationship
    project = relationship("Project", back_populates="assets")
