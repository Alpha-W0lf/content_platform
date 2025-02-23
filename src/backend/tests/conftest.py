"""
Pytest fixtures for backend tests.
"""
import pytest
import pytest_asyncio  # noqa: F401
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.backend.main import app
from src.backend.core.config import Settings  # Import Settings class
from src.backend.core.database import get_db
from src.backend.models.base import Base  # Import from models.base

import asyncio
import sys

# added to address a bug
if sys.platform == "win32" and sys.version_info >= (3, 8, 0):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Instantiate Settings
settings = Settings()  # type: ignore[call-arg]

# Use a separate test database
TEST_DATABASE_URL = settings.TEST_DATABASE_URL  # Access instance attribute
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(
    bind=test_engine, expire_on_commit=False, class_=AsyncSession
)

# Fixture to create and drop tables before/after each test
@pytest.fixture(scope="function")  # Use function scope for per-test isolation
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# Fixture for database session
@pytest.fixture(scope="function")
async def db_session(setup_database):  # Depends on setup_database
    await setup_database  # Ensure database is setup
    session = TestSessionLocal()
    yield session
    await session.rollback()  # Rollback after each test
    await session.close()

# Fixture for httpx AsyncClient (for making requests to your API)
@pytest.fixture(scope="function")
async def client(db_session: AsyncSession):  # Added explicit type hint
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client
    app.dependency_overrides.clear()  # cleanup

@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

# Fixture for celery config
@pytest.fixture(scope="session")
def celery_config():
    return {
        'broker_url': 'memory://',  # Use in-memory broker for tests
        'result_backend': None,      # Disable result backend
    }
