"""update project status enum

Revision ID: 7371c6d1fad0
Revises:
Create Date: 2025-02-16 05:11:00.000000

"""

from sqlalchemy import text
from sqlalchemy.engine import Connection

# revision identifiers, used by Alembic.
revision: str = "7371c6d1fad0"
down_revision: str | None = "a6a18453a7ab"
branch_labels: str | None = None
depends_on: str | None = None


from typing import Optional


def upgrade(connection: Optional[Connection] = None) -> None:
    if connection is None:
        from alembic import op

        connection = op.get_bind()

    # First create the enum type if it doesn't exist
    connection.execute(
        text(
            """
        DO $$ 
        BEGIN 
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'project_status') THEN
                CREATE TYPE project_status AS ENUM ('CREATED');
            END IF;
        END
        $$;
    """
        )
    )

    # Then add the new values
    queries = [
        "ALTER TYPE project_status ADD VALUE IF NOT EXISTS 'PROCESSING' AFTER 'CREATED'",
        "ALTER TYPE project_status ADD VALUE IF NOT EXISTS 'COMPLETED' AFTER 'PROCESSING'",
        "ALTER TYPE project_status ADD VALUE IF NOT EXISTS 'ERROR' AFTER 'COMPLETED'",
    ]
    for query in queries:
        connection.execute(text(query))


def downgrade(connection: Optional[Connection] = None) -> None:
    if connection is None:
        from alembic import op

        connection = op.get_bind()
    # Note: PostgreSQL does not support removing enum values
    pass
