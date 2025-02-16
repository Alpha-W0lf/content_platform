"""
Pytest fixtures for backend tests.
"""
import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.backend.main import app
from src.backend.core.config import settings
from src.backend.models import Base
from src.backend.core.database import get_db

# Create test engine using settings
test_engine = create_async_engine(
    settings.TEST_DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=0
)

TestSessionLocal = sessionmaker(
    bind=test_engine,
    expire_on_commit=False,
    class_=AsyncSession
)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def _setup_test_db():
    """Create test database objects and clean up after tests"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()

@pytest.fixture(autouse=True)
async def setup_database(_setup_test_db):
    """Create fresh tables before each test"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session(setup_database) -> AsyncSession:
    """Get a test database session"""
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.rollback()
        finally:
            await session.close()

@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncClient:
    """Get a test client for making API requests"""
    app.dependency_overrides[get_db] = lambda: db_session
    async with AsyncClient(app=app, base_url="http://test") as ac:
        try:
            yield ac
        finally:
            app.dependency_overrides.clear()