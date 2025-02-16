"""update_project_status_enum

Revision ID: 7371c6d1fad0
Revises: a6a18453a7ab
Create Date: 2025-02-16 05:11:28.927465+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '7371c6d1fad0'
down_revision: Union[str, None] = 'a6a18453a7ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the new enum type
    project_status = postgresql.ENUM('CREATED', 'PROCESSING', 'COMPLETED', 'ERROR', name='projectstatus', create_type=False)
    project_status.create(op.get_bind(), checkfirst=True)

    # Update the column to use the new enum with explicit casting
    op.execute('ALTER TABLE projects ALTER COLUMN status TYPE projectstatus USING status::text::projectstatus')
    op.execute('ALTER TABLE projects ALTER COLUMN status SET NOT NULL')
    
    # Drop the old enum type
    op.execute('DROP TYPE IF EXISTS project_status')


def downgrade() -> None:
    # Create the old enum type
    old_status = postgresql.ENUM('CREATED', 'PROCESSING', 'COMPLETED', 'ERROR', name='project_status', create_type=False)
    old_status.create(op.get_bind(), checkfirst=True)

    # Revert the column to use the old enum with explicit casting
    op.execute('ALTER TABLE projects ALTER COLUMN status TYPE project_status USING status::text::project_status')
    op.execute('ALTER TABLE projects ALTER COLUMN status DROP NOT NULL')
    
    # Drop the new enum type
    op.execute('DROP TYPE IF EXISTS projectstatus')