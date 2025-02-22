"""
Pytest fixtures for backend tests.
"""

import asyncio
from typing import AsyncGenerator, Generator

import logging
import pytest
import pytest_asyncio
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

test_engine: AsyncEngine = create_async_engine(
    settings.TEST_DATABASE_URL,  # Fixed case to match Settings class
    echo=False,
    future=True,
)

async_session = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def setup_database() -> AsyncGenerator[None, None]:
    async with test_engine.begin() as conn:
        # Create tables
        from src.backend.models.base import Base

        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        # Drop tables
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def db_session(setup_database):
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


logger = logging.getLogger(__name__)


@pytest.fixture(autouse=True)
async def cleanup_database(db_session: AsyncSession):
    """Clean up the test database before each test."""
    try:
        logger.info("Cleaning up database: truncating tables")
        # Clean up before test by truncating all tables
        await db_session.execute(text("TRUNCATE TABLE projects CASCADE"))
        await db_session.execute(text("TRUNCATE TABLE assets CASCADE"))
        await db_session.commit()
        # Start with a fresh transaction
        await db_session.begin()
        logger.info("Database cleanup complete")
        yield
    finally:
        logger.info("Rolling back transaction after cleanup")
        # Rollback transaction in case of errors
        await db_session.rollback()
