"""merge migrations

Revision ID: 4e3759c10b61
Revises: a6a18453a7ab, 7371c6d1fad0
Create Date: 2025-02-17 22:22:19.786957+00:00

"""

from typing import Sequence, Tuple, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.engine import Connection

# revision identifiers, used by Alembic.
revision: str = "4e3759c10b61"
down_revision: Tuple[str, str] = ("a6a18453a7ab", "7371c6d1fad0")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # This is a merge migration, no schema changes needed
    pass


def downgrade() -> None:
    # This is a merge migration, no schema changes needed
    pass
