"""
Pytest fixtures for backend tests.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from src.backend.main import app
from src.backend.core.config import settings
from src.backend.models import Base
from src.backend.core.database import get_db
from contextlib import asynccontextmanager

# Create test engine using settings
test_engine = create_async_engine(
    settings.TEST_DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=0
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

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
async def db_session() -> AsyncSession:
    """Get a test database session"""
    async with TestSessionLocal() as session:
        yield session

@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncClient:
    """Get a test client for making API requests"""
    @asynccontextmanager
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    client_instance = AsyncClient(app=app, base_url="http://test")
    yield client_instance
    await client_instance.aclose()
    app.dependency_overrides.clear()
