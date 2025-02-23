**The Wrong Approach (and Why)**

The current approach, while well-intentioned, has a few subtle but critical flaws:

*   **Overly Ambitious Testing:** Trying to test *everything* (API, models, tasks) at once, *before* ensuring the fundamental database setup is rock-solid, is making it hard to isolate problems.
*   **Missing Database Creation:** The `setup_database` fixture in `conftest.py` is missing the crucial step of creating the `test_content_platform` database *before* trying to create tables within it.
*   **Confusing Fixture Scope**: The scope of fixtures needs to be clarified.

**The Corrected Approach (Step-by-Step)**

We're going to focus on getting the database and model tests working *first*, then move on to the API and Celery tests. This creates a solid foundation.

**Step 1: Fix Database Initialization (Critical)**

We need to modify `src/backend/tests/conftest.py` to explicitly create the test database if it doesn't exist. We'll do this by leveraging the `postgres` database (which *does* exist by default) to create `test_content_platform`. We'll also make the `setup_database` fixture `session`-scoped, as we only need to create/drop tables once per test session, not once per test function.

```python
# src/backend/tests/conftest.py
import asyncio
import logging
import os
from typing import AsyncGenerator, Generator

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
from src.backend.models.asset import Asset  # noqa: F401
from src.backend.models.base import Base
from src.backend.models.project import Project  # noqa: F401

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Database Setup ---
TEST_DATABASE_URL = settings.TEST_DATABASE_URL  # Use settings

# Create async engine using the configured test database URL
test_engine: AsyncEngine = create_async_engine(
    TEST_DATABASE_URL,
    echo=True,  # Enable SQL logging
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
                f"SELECT 1 FROM pg_database WHERE datname = '{settings.TEST_DATABASE_URL.split('/')[-1]}'"
            )
        )
        if not database_exists:
            await conn.execute(
                text(f"CREATE DATABASE {settings.TEST_DATABASE_URL.split('/')[-1]}")
            )
            logger.info(f"Created database {settings.TEST_DATABASE_URL.split('/')[-1]}")

    await default_engine.dispose()


# Fixture to create and drop tables before/after the test session
@pytest.fixture(scope="session", autouse=True)
async def setup_database(create_test_database):  # Depend on create_test_database
    """Set up test database tables."""
    logger.info("Starting database setup...")
    try:
        async with test_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            logger.info("Database connection successful")
            logger.info("Dropping all existing tables...")
            await conn.run_sync(Base.metadata.drop_all)

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
        # Clean up after tests
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            logger.info("Database cleanup completed")


# Fixture for database session, function-scoped for per-test isolation
@pytest_asyncio.fixture(scope="function")
async def db_session(setup_database: None) -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session for tests."""
    async with async_session() as session:
        try:
            yield session
            await session.rollback()  # Rollback after each test
        except Exception as e:
            await session.rollback()  # Rollback in case of any exceptions
            raise
        finally:
            await session.close()


# Fixture for httpx AsyncClient (for making requests to your API), function-scoped
@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Test client fixture that uses the test database session."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest.fixture(scope="session", autouse=True)
def setup_test_env() -> None:
    """Set up test environment variables."""
    # Set default Redis password if not configured
    redis_password = settings.REDIS_PASSWORD or "testpassword"
    redis_url = f"redis://:{redis_password}@redis:6379/0"

    # Set Redis-related environment variables
    os.environ["REDIS_PASSWORD"] = redis_password
    os.environ["REDIS_URL"] = redis_url
    os.environ["CELERY_BROKER_URL"] = redis_url
    os.environ["CELERY_RESULT_BACKEND"] = redis_url

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

```

Key changes:

*   **`create_test_database` Fixture (New):** This fixture now explicitly creates the `test_content_platform` database *before* any tests run. It connects to the default `postgres` database to do this.  This is the *crucial* fix.
*   **Dependency Injection:** The `setup_database` fixture now depends on the `create_test_database` fixture, ensuring the database is created before tables.
*   **Scope Changes:**
    *   `setup_database` is now `scope="session"` and `autouse=True`.  We only need to create/drop the *tables* once per test session.
    *   `db_session` remains `scope="function"` to provide a fresh, isolated session for each test.
*   **Error Handling:** Added `try...except...finally` blocks to `db_session` and `setup_database` to handle potential errors during setup/teardown.
*   **`get_db` Override (Function Scope):**  The `client` fixture overrides `get_db` to use the `db_session`.  This is essential for dependency injection to work correctly in your tests.
*  **`event_loop` Fixture:** Added an event_loop fixture.
*  **`setup_test_env` Fixture:** Set up test environment variables.
*   **`autouse=True`:** Add `autouse=True` to the `setup_test_env` fixture.

**Step 2: Run the Model Tests (and ONLY the Model Tests)**

Now that your database setup is correct, run *just* the model tests:

```bash
docker-compose run api pytest -v src/backend/tests/test_models
```

These tests *should* now pass. If they don't, there's a problem with your model definitions or the test code itself, but it's *not* a database setup issue. Focus on the specific error messages from pytest.

**Step 3: Address Redis Configuration for Celery Tests (Secondary)**

You're also seeing `redis.exceptions.AuthenticationError` in your Celery tests.  This is a separate issue from the database problem, but it's good to address it now. The issue is that your test configuration isn't correctly providing the Redis password to Celery. We will add default values for Redis in `src/backend/core/config.py` to support tests.

```python
# src/backend/core/config.py
from typing import Optional

from pydantic import Field, ValidationInfo, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Content Platform"
    API_VERSION: str = "v0.0"
    DATABASE_URL: str = Field(
        default=(
            "postgresql+asyncpg://user:password@localhost:5432/"
            "content_platform?timezone=utc"
        )
    )
    TEST_DATABASE_URL: str = Field(default="")
    REDIS_URL: Optional[str] = "redis://:testpassword@localhost:6379/0" # ADDED
    REDIS_PASSWORD: Optional[str] = "testpassword" #ADDED

    CELERY_BROKER_URL: str = Field(default="redis://redis:6379/0")
    CELERY_RESULT_BACKEND: str = Field(default="redis://redis:6379/0")
    CLERK_SECRET_KEY: Optional[str] = None
    HEYGEN_API_KEY: Optional[str] = None

    # Add Clerk public configurations
    next_public_clerk_publishable_key: Optional[str] = None
    next_public_api_url: Optional[str] = None
    next_public_clerk_sign_in_url: Optional[str] = None
    next_public_clerk_sign_up_url: Optional[str] = None
    next_public_clerk_after_sign_in_url: Optional[str] = None
    next_public_clerk_after_sign_up_url: Optional[str] = None

    # Add Heygen credentials
    heygen_email: Optional[str] = None
    heygen_password: Optional[str] = None

    @field_validator("CELERY_BROKER_URL", "CELERY_RESULT_BACKEND", mode="before")
    def set_celery_urls(cls, v: Optional[str], info: ValidationInfo) -> str:
        if not v and "REDIS_URL" in info.data:
            redis_url = info.data.get("REDIS_URL")
            if redis_url is not None:
                return str(redis_url)
        return v or ""

    class Config:
        env_file = ".env"


settings = Settings()
```
Key Changes:

*   **Default Redis Credentials:** We provide default values for the `REDIS_URL` and `REDIS_PASSWORD` fields.

Now, update your `src/backend/tasks/project_tasks.py` file. Add the `bind=True` argument to `@celery_app.task` decorator. This allows you to use the self keyword in the `process_project` function. Also, you should be using `celery_app` for the redis test tasks.

```python
# src/backend/tasks/project_tasks.py
import logging
import os
from datetime import datetime
from typing import Any, Dict

import redis
from celery import Task
from sqlalchemy import select

from src.backend.core.database import AsyncSessionLocal
from src.backend.models.project import Project
from src.backend.schemas.project import ProjectStatus
from src.backend.tasks import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="test_broker_settings")
def test_broker_settings() -> Dict[str, Any]:
    """Test Redis broker settings and authentication independently.
    Returns a dictionary with test results and diagnostics."""
    results: Dict[str, Any] = {
        "status": "unknown",
        "redis_info": {},
        "connection_test": False,
        "auth_test": False,
        "diagnostics": [],  # Initialize diagnostics as a list
    }

    try:
        # Get broker URL components from Celery app
        broker_url = celery_app.conf.broker_url
        results["diagnostics"].append(f"Broker URL: {broker_url}")

        # Test direct Redis connection
        redis_client = redis.Redis.from_url(
            url=broker_url, socket_timeout=5, socket_connect_timeout=5
        )

        # Test basic connection
        if redis_client.ping():
            results["connection_test"] = True
            results["diagnostics"].append("Basic connection test (PING) successful")

        # Test authentication with credentials
        try:
            # Get credentials from URL
            credentials = broker_url.split("@")[0].split(":")
            if len(credentials) >= 3:
                username = credentials[1].split("//")[1]
                password = credentials[2]
                redis_client.execute_command("AUTH", username, password)
                results["auth_test"] = True
                results["diagnostics"].append("Authentication test successful")
        except redis.AuthenticationError as auth_err:
            results["diagnostics"].append(
                f"Authentication test failed: {str(auth_err)}"
            )
            raise

        # Get Redis info
        redis_info = redis_client.info()
        results["redis_info"] = {
            "version": redis_info.get("redis_version"),
            "clients": redis_info.get("connected_clients"),
            "memory_used": redis_info.get("used_memory_human"),
            "role": redis_info.get("role"),
            "connected_slaves": redis_info.get("connected_slaves", 0),
        }

        # Test pub/sub (important for Celery)
        pubsub = redis_client.pubsub()
        test_channel = "test_channel"
        pubsub.subscribe(test_channel)
        redis_client.publish(test_channel, "test message")
        message = pubsub.get_message(timeout=1)
        if message and message.get("type") == "subscribe":
            results["diagnostics"].append("Pub/Sub test successful")
        else:
            results["diagnostics"].append("Pub/Sub test failed or timed out")
        pubsub.unsubscribe(test_channel)

        # Overall status
        results["status"] = "success"
        logger.info("Broker settings test completed successfully")

    except redis.AuthenticationError as e:
        results["status"] = "auth_error"
        results["diagnostics"].append(f"Authentication error: {str(e)}")
        logger.error(f"Redis authentication error: {str(e)}")

    except redis.ConnectionError as e:
        results["status"] = "connection_error"
        results["diagnostics"].append(f"Connection error: {str(e)}")
        logger.error(f"Redis connection error: {str(e)}")

    except Exception as e:
        results["status"] = "error"
        results["diagnostics"].append(f"Unexpected error: {str(e)}")
        logger.exception("Unexpected error in test_broker_settings")

    return results


@celery_app.task(name="redis_interaction_test")
def redis_interaction_test() -> str:
    """A task to test Redis interaction."""
    try:
        # Get Redis configuration from environment
        redis_password = os.getenv("REDIS_PASSWORD")
        redis_host = os.getenv("REDIS_HOST", "redis")  # Default to 'redis'
        redis_port = int(os.getenv("REDIS_PORT", "6379"))  # Default to 6379
        redis_db = int(os.getenv("REDIS_DB", "0"))  # Default to 0

        # Try direct Redis connection
        r = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            password=redis_password,
            decode_responses=True,
        )
        if not r.ping():
            raise redis.ConnectionError("Redis PING failed")

        # Try basic operations
        test_key = f"test:connection:{datetime.utcnow().isoformat()}"
        r.set(test_key, "testvalue", ex=60)  # 60 second expiry
        value = r.get(test_key)
        if value != "testvalue":
            raise Exception(
                f"Redis value mismatch. Expected: testvalue, got: {value}"
            )

        return "Success"

    except redis.AuthenticationError as e:
        logger.error(f"Redis authentication failed: {str(e)}")
        return f"Auth Error: {str(e)}"
    except redis.ConnectionError as e:
        logger.error(f"Redis connection error: {str(e)}")
        return f"Connection Error: {str(e)}"
    except Exception as e:
        logger.exception(f"Unexpected error in redis_interaction_test: {str(e)}")
        return f"Error: {str(e)}"


@celery_app.task(bind=True, name="celery_debug_task")
def celery_debug_task(self, arg1: int, arg2: int) -> int:
    """Test task that confirms celery is working."""
    logger.debug(f"Executing task {self.request.id} with args: {arg1}, {arg2}")
    return arg1 + arg2


@celery_app.task(bind=True, name="process_project")
def process_project(self: Task, project_id: str) -> None:
    """Process a project (placeholder)."""
    logger.info(f"Starting process_project for project_id: {project_id}")

    # Create a new database session for this task
    async def _process():
        async with AsyncSessionLocal() as db:
            try:
                # Get the project
                result = await db.execute(
                    select(Project).where(Project.id == project_id)
                )
                project = result.scalar_one_or_none()

                if project is None:
                    logger.error(f"Project not found: {project_id}")
                    # Update project status to ERROR
                    return

                project.status = ProjectStatus.PROCESSING  # Use the enum member
                await db.commit()
                await db.refresh(project)
                logger.info(f"Project {project_id} status updated to PROCESSING")

                # Simulate work (replace with actual project processing logic)
                import time

                time.sleep(5)

                project.status = ProjectStatus.COMPLETED  # Use the enum member
                await db.commit()
                logger.info(f"Project {project_id} status updated to COMPLETED")

            except Exception as e:
                logger.exception(f"Error processing project {project_id}")
                await db.rollback()
                if project:
                    project.status = (
                        ProjectStatus.ERROR
                    )  # Use enum member, and handle None
                    await db.commit()
                # Re-raise the exception so Celery knows the task failed
                raise

    asyncio.run(_process())

```
Key Changes:
* Added the redis test tasks.
* Added `bind=True` argument to `@celery_app.task` decorator
* Updated `process_project`

Now run:

```bash
docker-compose run api pytest -v src/backend/tests/test_tasks
```

**Step 4: Run API Tests (Selectively)**

Once your model tests pass, run the API tests that *don't* depend on Celery:

```bash
docker-compose run api pytest -v src/backend/tests/test_api
```

**Step 5: Run All Tests (Once Everything Else Works)**

Finally, when you're confident that the database and basic API functionality are working, run the full test suite:

```bash
docker-compose run api pytest -v
```

**Troubleshooting Strategy (If Tests Still Fail)**

1.  **Read the Error Messages Carefully:** The full traceback from pytest is your best friend. Pay close attention to the line numbers and the specific error message.
2.  **Isolate:** If a test fails, try running it in isolation: `pytest -v src/backend/tests/test_models/test_project.py::test_project_creation`.
3.  **Print Statements (Temporarily):** Add `print()` statements to your test functions and/or your application code to inspect the values of variables at different points. This is a quick way to see what's happening.  Make sure you remove these before committing.
4. **Check the Database Directly:**

    ```bash
    docker-compose exec postgres psql -U user -d test_content_platform
    \dt  # List tables
    SELECT * FROM projects;
    ```

By following this focused approach, you should be able to break the debugging cycle and make consistent progress. The key is to build up from a solid foundation (database and models) before tackling more complex interactions. Remember to remove the temporary debugging code (print statements) once you've resolved the issues.
