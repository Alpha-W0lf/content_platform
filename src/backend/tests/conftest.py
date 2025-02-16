"""
Pytest fixtures for backend tests.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.backend.main import app
from src.backend.core.config import settings
from src.backend.models import Base  # Import from models package
from src.backend.core.database import get_db

# Create test engine using settings
test_engine = create_async_engine(
    settings.TEST_DATABASE_URL,
    echo=True,
    # These settings help ensure clean test isolation
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=0
)

TestSessionLocal = sessionmaker(
    bind=test_engine,
    expire_on_commit=False,
    class_=AsyncSession
)

@pytest.fixture(scope="session", autouse=True)
async def setup_test_db():
    """Create test database objects and clean up after tests"""
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield  # Run the tests
    
    # Clean up - drop all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    # Dispose the engine
    await test_engine.dispose()

@pytest.fixture(scope="function")
async def setup_database():
    """Create fresh tables before each test and clean up after"""
    # Clear any existing data
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Clean up after test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session():
    """Get a test database session"""
    async with TestSessionLocal() as session:
        yield session
        await session.close()

@pytest.fixture(scope="module")
async def client():
    """Get a test client for making API requests"""
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c

@pytest.fixture(scope="function", autouse=True)
async def override_dependencies(db_session):
    """Override database dependency for testing"""
    async def override_get_db():
        try:
            yield db_session
        finally:
            await db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    # Store original URL
    original_url = settings.DATABASE_URL
    # Override with test URL
    settings.DATABASE_URL = settings.TEST_DATABASE_URL
    
    yield
    
    # Cleanup
    app.dependency_overrides.clear()
    # Restore original URL
    settings.DATABASE_URL = original_url