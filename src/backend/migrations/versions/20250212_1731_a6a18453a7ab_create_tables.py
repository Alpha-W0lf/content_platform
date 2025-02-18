"""Create tables

Revision ID: a6a18453a7ab
Revises:
Create Date: 2025-02-12 17:31:03.159223+00:00

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID
from src.backend.schemas.project import ProjectStatus

# revision identifiers, used by Alembic.
revision: str = "a6a18453a7ab"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade(connection=None) -> None:
    op.create_table(
        "projects",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("topic", sa.String, nullable=False),
        sa.Column(
            "status",
            sa.Enum(ProjectStatus),
            nullable=False,
            default=ProjectStatus.CREATED,
        ),
        sa.Column("name", sa.String, nullable=True),
        sa.Column("notes", sa.String, nullable=True),
        sa.Column("created_at", sa.DateTime, default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime,
            default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )

    op.create_table(
        "assets",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "project_id", UUID(as_uuid=True), sa.ForeignKey("projects.id")
        ),
        sa.Column(
            "asset_type",
            sa.Enum("script", "narration", "video", "image", "slide", name="asset_type"),
            nullable=False
        ),
        sa.Column("path", sa.String, nullable=False),
        sa.Column("approved", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime, default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime,
            default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )



def downgrade(connection=None) -> None:
    op.drop_table("assets")
    op.drop_table("projects")
