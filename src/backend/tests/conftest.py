"""
Pytest fixtures for backend tests.
"""

import asyncio
import logging
import os
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.backend.core.config import settings
from src.backend.core.database import get_db
from src.backend.main import app
from src.backend.models.asset import Asset  # noqa: F401
from src.backend.models.base import Base
from src.backend.models.project import Project  # noqa: F401

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create test engine using the configured test database URL
test_engine: AsyncEngine = create_async_engine(
    settings.TEST_DATABASE_URL,
    echo=True,  # Enable SQL logging
    future=True,
)

async_session = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session", autouse=True)
def setup_test_env() -> None:
    """Set up test environment variables."""
    # Set default Redis password if not configured
    redis_password = settings.REDIS_PASSWORD or "testpassword"
    redis_url = f"redis://:{redis_password}@redis:6379/0"

    # Set Redis-related environment variables
    os.environ["REDIS_PASSWORD"] = redis_password
    os.environ["REDIS_URL"] = redis_url
    os.environ["CELERY_BROKER_URL"] = redis_url
    os.environ["CELERY_RESULT_BACKEND"] = redis_url


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def setup_database() -> AsyncGenerator[None, None]:
    """Set up test database tables."""
    logger.info("Starting database setup...")
    try:
        # Ensure we have a connection to the database
        async with test_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            logger.info("Database connection successful")

            # Drop all tables to ensure clean state
            logger.info("Dropping all existing tables...")
            await conn.run_sync(Base.metadata.drop_all)

            # Run migrations
            logger.info("Running migrations...")
            await conn.commit()  # Commit the transaction before running migrations

        # Run migrations synchronously
        logger.info("Configuring Alembic...")
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("script_location", "src/backend/migrations")
        alembic_cfg.set_main_option("sqlalchemy.url", str(settings.TEST_DATABASE_URL))
        alembic_cfg.attributes["db"] = "test"  # Set the db attribute for test database
        logger.info("Running Alembic upgrade to head...")
        try:
            command.upgrade(alembic_cfg, "head")
            logger.info("Alembic upgrade completed successfully")
        except Exception as e:
            logger.error(f"Error during Alembic upgrade: {e}")
            raise

        # Verify tables were created
        async with test_engine.connect() as conn:
            result = await conn.execute(
                text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
            )
            tables = [row[0] for row in result]
            logger.info(f"Created tables: {tables}")

            # Verify table structure
            for table in ["projects", "assets"]:
                if table not in tables:
                    raise Exception(f"Required table '{table}' was not created")
                columns = await conn.execute(
                    text(
                        "SELECT column_name, data_type FROM information_schema.columns "
                        f"WHERE table_name = '{table}'"
                    )
                )
                logger.info(f"Columns in {table}: {[row for row in columns]}")

        logger.info("Database setup completed successfully")
        yield
    except Exception as e:
        logger.error(f"Error during database setup: {e}")
        raise
    finally:
        # Clean up after tests
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            logger.info("Database cleanup completed")


@pytest_asyncio.fixture(scope="function")
async def db_session(setup_database: None) -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session for tests."""
    async with async_session() as session:
        yield session
        await session.rollback()  # Rollback after each test


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Test client fixture that uses the test database session."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
async def cleanup_database(db_session: AsyncSession) -> AsyncGenerator[None, None]:
    """Clean up test database tables before each test."""
    try:
        # Start with a clean slate
        await db_session.execute(text("TRUNCATE TABLE projects CASCADE"))
        await db_session.execute(text("TRUNCATE TABLE assets CASCADE"))
        await db_session.commit()
        yield
    except Exception as e:
        logger.error(f"Error during database cleanup: {e}")
        await db_session.rollback()
        raise
