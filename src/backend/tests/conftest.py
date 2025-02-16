"""
Pytest fixtures for backend tests.
"""

from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.backend.core.config import settings
from src.backend.main import app
from src.backend.models import Base

# Create test engine using settings
test_engine = create_async_engine(
    str(settings.TEST_DATABASE_URL),  # Convert to string to handle type checking
    echo=True,
    pool_pre_ping=True,
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(autouse=True)
async def setup_database() -> AsyncGenerator[None, None]:
    """Set up a clean test database for each test"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a test database session"""
    async with TestSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Get a test client"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
