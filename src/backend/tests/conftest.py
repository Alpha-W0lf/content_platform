"""
Pytest fixtures for backend tests.
"""

from dotenv import load_dotenv
import asyncio
import logging
import os

load_dotenv()
os.environ["REDIS_PASSWORD"] = os.environ.get("REDIS_PASSWORD", "testpassword")
os.environ["REDIS_URL"] = (
    "redis://:testpassword@localhost:6379/0"  # Changed to localhost
)
os.environ["CELERY_BROKER_URL"] = os.environ["REDIS_URL"]
os.environ["CELERY_RESULT_BACKEND"] = os.environ["REDIS_URL"]
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
from src.backend.models import asset  # noqa: F401
from src.backend.models import base
from src.backend.models import project  # noqa: F401

load_dotenv()
logger = logging.getLogger(__name__)

# Configure logging to be less verbose
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("alembic").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)

logger.info(f"TEST_DATABASE_URL: {settings.TEST_DATABASE_URL}")
if not settings.TEST_DATABASE_URL:
    raise ValueError("TEST_DATABASE_URL is not set in settings")

test_engine: AsyncEngine = create_async_engine(
    settings.TEST_DATABASE_URL,
    echo=False,  # Disabled SQL echo
    future=True,
)

async_session = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Fixture to create the test database if it does not exist
@pytest.fixture(scope="session", autouse=True)
async def create_test_database():
    """Create test database if it doesn't exist"""
    # Use a connection to the 'postgres' database to create test_content_platform
    default_db_url = settings.DATABASE_URL.replace(
        "content_platform", "postgres"
    )  # Replace databasename
    default_engine = create_async_engine(default_db_url, isolation_level="AUTOCOMMIT")

    async with default_engine.connect() as conn:
        database_exists = await conn.scalar(
            text(
                "SELECT 1 FROM pg_database WHERE datname = '"
                f"{settings.TEST_DATABASE_URL.split('/')[-1]}'"
            )
        )
        if not database_exists:
            await conn.execute(
                text(f"CREATE DATABASE {settings.TEST_DATABASE_URL.split('/')[-1]}")
            )
            logger.info(
                f"Created database " f"{settings.TEST_DATABASE_URL.split('/')[-1]}"
            )

    await default_engine.dispose()


# Fixture to create and drop tables before/after test session
@pytest.fixture(scope="session", autouse=True)
async def setup_database(create_test_database):  # Depend on create_test_database
    """Set up test database tables."""
    logger.info("Starting database setup...")
    try:
        async with test_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            logger.info("Database connection successful")
            logger.info("Dropping all existing tables...")
            await conn.run_sync(base.Base.metadata.drop_all)

            # Run migrations
            logger.info("Running migrations...")
            await conn.commit()

        logger.info("Configuring Alembic...")
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("script_location", "src/backend/migrations")
        alembic_cfg.set_main_option("sqlalchemy.url", str(settings.TEST_DATABASE_URL))
        alembic_cfg.attributes["db"] = "test"
        logger.info("Running Alembic upgrade to head...")
        command.upgrade(alembic_cfg, "head")
        logger.info("Alembic upgrade completed successfully")

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
        logger.info("Cleaning up database...")
        async with test_engine.begin() as conn:
            await conn.run_sync(base.Base.metadata.drop_all)
        logger.info("Database cleanup completed")


# Fixture for database session, function-scoped for per-test isolation
@pytest_asyncio.fixture(scope="function")
async def db_session(setup_database):
    """Provide a database session for tests."""
    async with async_session() as session:
        yield session
        await session.rollback()


# Fixture for httpx AsyncClient (for making requests to your API), function-scoped
@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession):
    """Test client fixture that uses the test database session."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
