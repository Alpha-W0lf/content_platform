import uuid
from datetime import datetime, timezone
from typing import Literal

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Asset(Base):
    __tablename__ = "assets"

    # Required fields without defaults should come first
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id")
    )
    asset_type: Mapped[Literal["script", "narration", "video", "image", "slide"]] = (
        mapped_column(
            SQLEnum("script", "narration", "video", "image", "slide", name="asset_type")
        )
    )
    path: Mapped[str] = mapped_column(String, nullable=False)

    # Optional fields with defaults come after
    approved: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships at the end
    project = relationship("Project", back_populates="assets")
