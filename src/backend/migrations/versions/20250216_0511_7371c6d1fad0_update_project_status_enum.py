"""update project status enum

Revision ID: 7371c6d1fad0
Revises:
Create Date: 2025-02-16 05:11:00.000000

"""

from sqlalchemy import text
from sqlalchemy.engine import Connection

# revision identifiers, used by Alembic.
revision: str = "7371c6d1fad0"
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None


def upgrade(connection: Connection) -> None:
    connection.execute(
        text(
            """
        ALTER TYPE project_status
        ADD VALUE IF NOT EXISTS 'PROCESSING' AFTER 'CREATED';
        ALTER TYPE project_status
        ADD VALUE IF NOT EXISTS 'COMPLETED' AFTER 'PROCESSING';
        ALTER TYPE project_status
        ADD VALUE IF NOT EXISTS 'ERROR' AFTER 'COMPLETED';
    """
        )
    )


def downgrade(connection: Connection) -> None:
    # Note: PostgreSQL does not support removing enum values
    pass
