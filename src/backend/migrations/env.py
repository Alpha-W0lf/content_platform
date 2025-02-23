import sys
import os
import asyncio
from pathlib import Path  # Import pathlib
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
from alembic.runtime.migration import MigrationContext

# ---  Correct Path Calculation (using pathlib) ---
# Get the absolute path to the current file (env.py)
current_file = Path(__file__).resolve()
# Get the parent directory (migrations), then its parent (backend), then its parent (src)
src_path = current_file.parent.parent.parent
# Add the 'src' directory to sys.path
sys.path.insert(0, str(src_path))
# --- End of Path Calculation ---

# --- Imports after modifying sys.path ---
from src.backend.core.config import settings  # Now this will work!
from src.backend.models import Base  # And this!


# --- Alembic Config ---
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def get_url() -> str:
    """Get the database URL based on the context."""
    if hasattr(config, "attributes") and config.attributes.get("db") == "test":
        return settings.TEST_DATABASE_URL
    return settings.DATABASE_URL

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = create_async_engine(get_url())

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())