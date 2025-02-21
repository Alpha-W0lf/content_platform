"""
Pytest fixtures for backend tests.
"""
import asyncio
from collections.abc import AsyncGenerator, Generator
import pytest_asyncio
import pytest
from httpx import AsyncClient
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
    settings.TEST_DATABASE_URL,
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


@pytest_asyncio.fixture(scope="session")
async def setup_database() -> AsyncGenerator[None, None]:
    async with test_engine.begin() as conn:
        # Create tables
        from src.backend.models.base import Base
        await conn.run_sync(Base.metadata.create_all)
    yield None
    async with test_engine.begin() as conn:
        # Drop tables
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(name="db_session")
async def db_session(setup_database: None) -> AsyncGenerator[AsyncSession, None]:
    """
    Create a fresh database session for a test.
    Returns an AsyncSession via AsyncGenerator for proper typing and cleanup.
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Test client fixture that uses the test database session."""
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
