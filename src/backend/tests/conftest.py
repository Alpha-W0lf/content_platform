"""
Pytest fixtures for backend tests.
"""
import pytest
import pytest_asyncio
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

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    """Create test database objects and clean up after tests"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()

@pytest_asyncio.fixture(scope="function")
async def setup_database():
    """Create fresh tables before each test and clean up after"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    """Get a test database session"""
    session = TestSessionLocal()
    try:
        yield session
    finally:
        await session.close()

@pytest_asyncio.fixture
async def client() -> AsyncClient:
    """Get a test client for making API requests"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest_asyncio.fixture(autouse=True)
async def override_dependencies(db_session: AsyncSession):
    """Override database dependency for testing"""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()