"""
Pytest fixtures for backend tests.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.backend.main import app
from src.backend.core.config import settings
from src.backend.core.database import Base, get_db

# Use a separate test database
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/test_content_platform"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestSessionLocal = sessionmaker(
    bind=test_engine,
    expire_on_commit=False,
    class_=AsyncSession
)

@pytest.fixture(scope="function")
async def setup_database():
    """Create tables before test and drop them after"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
async def db_session():
    """Get a test database session"""
    async with TestSessionLocal() as session:
        yield session

@pytest.fixture(scope="module")
async def client():
    """Get a test client for making API requests"""
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c

@pytest.fixture(scope="function", autouse=True)
def override_dependencies(db_session):
    """Override database dependency for testing"""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    settings.DATABASE_URL = TEST_DATABASE_URL
    yield
    app.dependency_overrides.clear()