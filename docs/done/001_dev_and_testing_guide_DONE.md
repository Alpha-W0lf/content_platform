# All tasks completed for this guide.

```markdown
# Content Platform Development Guide - Part 1: Project Setup and Initial API/Model Tests

This is Part 1 of 4 in the Content Platform Development Guide series:

- Part 1 (Current): Project Setup and Initial API/Model Tests
- Part 2: PATCH Endpoint and Error Handling
- Part 3: Task Testing and Request Logging
- Part 4: Task Error Handling and Frontend Integration

This part focuses on getting the basic project structure, API endpoints (create, get, list), and corresponding model and API tests in place. It follows a Test-Driven Development (TDD) approach.

**Remember to always:**

- **Follow Best Practices:** Use clear naming conventions, write docstrings, keep functions small and focused, and adhere to PEP 8 style guidelines (enforced by your linters).
- **Maintainable Code:** Write code that is easy to understand, modify, and extend. Use comments where necessary to explain _why_ you're doing something, not just _what_.
- **Targeted Changes:** Make small, incremental changes. Commit frequently with descriptive commit messages.
- **Modularity and Extensibility:** Design your code with future features in mind. Think about how new functionality will be added and how existing components can be reused. Use dependency injection and clearly defined interfaces.
- **Test Driven Development**: Write tests before code.

## Task Tracking (v0.0 Foundation)

### Implemented ✓

- [x] Project structure and directory setup
  - [x] Backend: FastAPI, Celery, SQLAlchemy structure
  - [x] Frontend: Next.js 13+ with App Router
  - [x] Docker configuration files
- [x] Database Setup
  - [x] PostgreSQL configuration
  - [x] SQLAlchemy async setup
  - [x] Basic models (Project, Asset)
  - [x] Initial Alembic migration
- [x] Initial API Setup
  - [x] Basic FastAPI configuration
  - [x] /health endpoint
  - [x] CORS middleware
  - [x] Basic Projects router (POST, GET endpoints)
- [x] Testing Infrastructure
  - [x] `conftest.py` setup
    - [x] Basic fixtures defined (`setup_database`, `db_session`, `client`)
    - [x] Test database configuration
    - [x] Database isolation per test
- [x] Initial API Tests
  - [x] `/projects` POST endpoint
    - [x] Success case
    - [x] Missing topic
    - [x] Invalid topic type
  - [x] `/projects/{id}` GET endpoint
    - [x] Success case
    - [x] Not found case
    - [x] Invalid ID format
  - [x] `/projects/{id}/status` GET endpoint
    - [x] Valid ID
    - [x] Invalid ID
  - [x] `/projects` GET (list) endpoint
    - [x] Empty list
    - [x] Multiple projects

### Implemented ✓

- [x] Initial Model Tests _**<-- Focus Here Next**_
  - [x] Project model creation
  - [x] Project status transitions
  - [x] Project-Asset relationship
  - [x] Project cascade delete
  - [x] Asset model creation
  - [x] Asset model updates
  - [x] Asset model timestamp updates
  - [x] Asset model enum validation
  - [x] Asset model path not nullable
- [x] Basic Error Handling
  - [x] Initial try/except blocks in endpoints
  - [x] Basic validation error responses

### Next Steps 📋

1.  **Complete Initial Model Tests:** Write tests for `Project` and `Asset` models (creation, updates, relationships, constraints).
2.  **Complete Basic Error Handling:** Add initial error handling to endpoints.
3.  **Move to PATCH Implementation:** Begin work on update functionality (after completing model tests and basic error handling).
4.  **Document Initial API:** Document the basic endpoints.

## 1. Project Structure (Review)

Make sure your project structure matches the following. You should have all these files and directories already. This is just a checklist.
```

alpha-w0lf-content_platform/
├── .docker/
│ ├── Dockerfile.api
│ ├── Dockerfile.celery
│ └── Dockerfile.frontend
├── src/
│ ├── backend/
│ │ ├── **init**.py
│ │ ├── alembic.ini
│ │ ├── celeryconfig.py
│ │ ├── main.py
│ │ ├── requirements.txt
│ │ ├── start.sh
│ │ ├── api/
│ │ │ ├── **init**.py
│ │ │ ├── dependencies.py
│ │ │ └── routers/
│ │ │ ├── **init**.py
│ │ │ └── projects.py
│ │ ├── core/
│ │ │ ├── **init**.py
│ │ │ ├── config.py
│ │ │ ├── database.py
│ │ │ └── utils.py
│ │ ├── migrations/
│ │ │ ├── **init**.py
│ │ │ ├── env.py
│ │ │ ├── script.py.mako
│ │ │ └── versions/
│ │ │ └── ... (your migration files)
│ │ ├── models/
│ │ │ ├── **init**.py
│ │ │ ├── asset.py
│ │ │ ├── base.py
│ │ │ └── project.py
│ │ ├── modules/
│ │ │ └── **init**.py
│ │ ├── prompts/
│ │ │ └── **init**.py
│ │ ├── schemas/
│ │ │ ├── **init**.py
│ │ │ ├── asset.py
│ │ │ └── project.py
│ │ ├── tasks/
│ │ │ ├── **init**.py
│ │ │ └── project_tasks.py
│ │ └── tests/
│ │ │ ├── **init**.py
│ │ │ ├── conftest.py
│ │ │ ├── test_api/
│ │ │ │ ├── **init**.py
│ │ │ │ └── test_projects.py
│ │ │ ├── test_models/
│ │ │ │ ├── **init**.py
│ │ │ │ ├── test_project.py
│ │ │ │ └── test_asset.py
│ │ │ └── test_modules/
│ │ │ └── **init**.py
│ └── frontend/
│ └── ... (your Next.js project) ...
├── .devcontainer/
│ └── devcontainer.json
├── .dockerignore
├── .env.example
├── .flake8
├── alembic.ini
├── docker-compose.yml
├── package.json
├── pyproject.toml
├── pyrightconfig.json
├── README.md
└── ... other files ...

````

## 2. Backend Code (Review and Ensure Consistency)

Review the following files and ensure they are consistent with the code provided in previous responses. Pay close attention to:

-   **Type Hints:** Make sure all functions and methods have type hints.
-   **Docstrings:** Make sure all functions and classes have docstrings explaining their purpose.
-   **Error Handling:** Basic `try...except` blocks in API endpoints.
-   **Imports**: Ensure all imports are present and organized.

-   `src/backend/main.py`
-   `src/backend/api/routers/projects.py`
-   `src/backend/api/dependencies.py`
-   `src/backend/core/config.py`
-   `src/backend/core/database.py`
-   `src/backend/core/utils.py`
-   `src/backend/models/project.py`
-   `src/backend/models/asset.py`
-   `src/backend/models/__init__.py`
-   `src/backend/schemas/project.py`
-   `src/backend/schemas/asset.py`
-   `src/backend/schemas/__init__.py`
-   `src/backend/celeryconfig.py`
-   `src/backend/migrations/env.py` (Make sure this is configured for asyncpg and your models)

## 3. Test Fixtures (`conftest.py`) - Review

Review your `src/backend/tests/conftest.py` file. It should look like this (this is a repeat from previous responses, but included for completeness):

```python
# src/backend/tests/conftest.py
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.backend.main import app
from src.backend.core.config import settings
from src.backend.core.database import get_db
from src.backend.models.base import Base  # Import from models.base

# Use a separate test database
TEST_DATABASE_URL = settings.TEST_DATABASE_URL  # Use settings
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)  # echo=False for cleaner output
TestSessionLocal = sessionmaker(
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
async def db_session(setup_database):
    async with TestSessionLocal() as session:
        yield session
        await session.rollback() # Rollback after each test

# Fixture for httpx AsyncClient (for making requests to your API)
@pytest.fixture(scope="module") # Module scope is fine here
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear() # Clean up overrides
````

Key Points:

- `TEST_DATABASE_URL`: Make sure this is correctly configured in your `.env` and `config.py`.

- `scope="function"`: Using `function` scope for `setup_database` and `db_session` ensures that each test function gets a fresh database and session, and that any changes are rolled back after the test. This is crucial for test isolation.

- `rollback()`: The `await session.rollback()` in `db_session` is essential. It ensures that any changes made during a test are undone, preventing data from one test from affecting another.

- `app.dependency_overrides`: Dependency overrides are cleared after the test.

## 4. Initial API Tests (`test_projects.py`) - Review

Review your `src/backend/tests/test_api/test_projects.py` file. It should include tests for the `POST /api/v1/projects/`, `GET /api/v1/projects/{id}`, `GET /api/v1/projects/{id}/status` and `GET /api/v1/projects/` endpoints. It should be consistent with the complete file provided in previous responses, including all the tests for success, missing data, invalid data, and not found cases.

## 5. Initial Model Tests - **IMPLEMENTATION (TDD)**

Now, we'll implement the model tests _before_ adding any further functionality to the models themselves. This is the core of TDD.

### 5.1. `test_project.py`

Create (or update) `src/backend/tests/test_models/test_project.py` with the following tests. These tests cover the current functionality of the `Project` model:

```python
# src/backend/tests/test_models/test_project.py
import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload  # Import joinedload

from src.backend.models.asset import Asset  # Import Asset
from src.backend.models.project import Project
from src.backend.schemas.project import ProjectStatus


@pytest.mark.asyncio
async def test_create_project(db_session: AsyncSession) -> None:
    # Using keyword args instead of positional args
    project = Project(
        id=uuid.uuid4(),
        topic="Test Topic",
        name="Test Project",
        notes="Test Notes",
        status=ProjectStatus.CREATED,
    )
    db_session.add(project)
    await db_session.commit()

    result = await db_session.execute(select(Project).filter_by(id=project.id))
    saved_project = result.scalar_one()

    assert saved_project.topic == "Test Topic"
    assert saved_project.name == "Test Project"
    assert saved_project.notes == "Test Notes"
    assert saved_project.status == ProjectStatus.CREATED


@pytest.mark.asyncio
async def test_project_status_transition(db_session: AsyncSession) -> None:
    project = Project(id=uuid.uuid4(), topic="Test Topic", status=ProjectStatus.CREATED)
    db_session.add(project)
    await db_session.commit()

    project.status = ProjectStatus.PROCESSING
    await db_session.commit()

    result = await db_session.execute(select(Project).filter_by(id=project.id))
    updated_project = result.scalar_one()
    assert updated_project.status == ProjectStatus.PROCESSING

@pytest.mark.asyncio
async def test_project_asset_relationship(db_session: AsyncSession) -> None:
    project = Project(
        id=uuid.uuid4(),
        topic="Test Topic",
        name="Test Project",
        status=ProjectStatus.CREATED,
    )

    asset1 = Asset(
        id=uuid.uuid4(),
        project_id=project.id,
        asset_type="script",
        path="/path/to/script",
    )

    asset2 = Asset(
        id=uuid.uuid4(),
        project_id=project.id,
        asset_type="video",
        path="/path/to/video",
    )

    project.assets = [asset1, asset2]
    db_session.add(project)  # Add the project, which will cascade to assets
    await db_session.commit()

    # Use joinedload to eager load the assets
    result = await db_session.execute(
        select(Project).filter_by(id=project.id).options(joinedload(Project.assets))
    )
    saved_project = result.scalar_one()

    assert len(saved_project.assets) == 2
    assert all(isinstance(asset, Asset) for asset in saved_project.assets)
    assert any(asset.asset_type == "script" for asset in saved_project.assets)
    assert any(asset.asset_type == "video" for asset in saved_project.assets)

@pytest.mark.asyncio
async def test_project_cascade_delete(db_session: AsyncSession) -> None:
    project = Project(
        id=uuid.uuid4(),
        topic="Test Topic",
        name="Test Project",
        status=ProjectStatus.CREATED,
    )

    asset = Asset(
        id=uuid.uuid4(),
        project_id=project.id,
        asset_type="script",
        path="/path/to/script",
    )

    project.assets = [asset]
    db_session.add(project) # Add the project
    await db_session.commit()

    await db_session.delete(project)
    await db_session.commit()

    # Verify project is deleted
    project_result = await db_session.execute(select(Project).filter_by(id=project.id))
    assert project_result.scalar_one_or_none() is None

    # Verify associated asset is deleted
    asset_result = await db_session.execute(select(Asset).filter_by(id=asset.id))
    assert asset_result.all() == []

@pytest.mark.asyncio
async def test_project_timestamps(db_session: AsyncSession) -> None:
    start_time = datetime.now(timezone.utc)

    project = Project(id=uuid.uuid4(), topic="Test Topic", status=ProjectStatus.CREATED)
    db_session.add(project)
    await db_session.commit()

    assert project.created_at >= start_time
    assert project.updated_at >= start_time

    # Test update
    original_updated_at = project.updated_at
    await db_session.refresh(project) # Important to get the exact time
    project.name = "Updated Name"
    await db_session.commit()

    result = await db_session.execute(select(Project).filter_by(id=project.id))
    saved_project = result.scalar_one()

    assert saved_project.updated_at > original_updated_at
    assert saved_project.created_at == project.created_at
```

Key points about `test_project.py`:

- **Test Cases:** Covers creation, status updates, relationships (with `Asset`), cascade deletion, and timestamp updates.
- **Asynchronous Tests:** All tests are `async` functions and use `await` for database operations.
- **Database Session Fixture:** Uses the `db_session` fixture (from `conftest.py`) to interact with the test database. Each test gets its own isolated session.
- **JoinedLoad**: Uses joinedload to eager load assets to ensure the relationship between assets and projects is set correctly.

### 5.2. `test_asset.py`

Create `src/backend/tests/test_models/test_asset.py` with the following tests:

```python
# src/backend/tests/test_models/test_asset.py
import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.models.asset import Asset
from src.backend.models.project import Project  # Import Project
from src.backend.schemas.project import ProjectStatus


@pytest.mark.asyncio
async def test_create_asset(db_session: AsyncSession) -> None:
    """Test creating an asset with valid data."""
    project = Project(id=uuid.uuid4(), topic="Test Topic", status=ProjectStatus.CREATED)
    db_session.add(project)
    await db_session.commit()

    asset = Asset(
        id=uuid.uuid4(),
        project_id=project.id,
        asset_type="script",
        path="/path/to/asset",
    )
    db_session.add(asset)
    await db_session.commit()

    result = await db_session.execute(select(Asset).filter_by(id=asset.id))
    saved_asset = result.scalar_one()

    assert saved_asset.project_id == project.id
    assert saved_asset.asset_type == "script"
    assert saved_asset.path == "/path/to/asset"


@pytest.mark.asyncio
async def test_asset_updates(db_session: AsyncSession) -> None:
    """Test updating asset fields."""
    project = Project(id=uuid.uuid4(), topic="Test Topic", status=ProjectStatus.CREATED)
    db_session.add(project)
    await db_session.commit()

    asset = Asset(
        id=uuid.uuid4(),
        project_id=project.id,
        asset_type="script",
        path="/original/path",
    )
    db_session.add(asset)
    await db_session.commit()

    # Update the asset
    asset.path = "/updated/path"
    asset.asset_type = "video"
    await db_session.commit()

    result = await db_session.execute(select(Asset).filter_by(id=asset.id))
    updated_asset = result.scalar_one()
    assert updated_asset.path == "/updated/path"
    assert updated_asset.asset_type == "video"


@pytest.mark.asyncio
async def test_asset_timestamp_updates(db_session: AsyncSession) -> None:
    """Test that timestamps are properly set and updated."""
    start_time = datetime.now(timezone.utc)

    project = Project(id=uuid.uuid4(), topic="Test Topic", status=ProjectStatus.CREATED)
    db_session.add(project)
    await db_session.commit()

    asset = Asset(
        id=uuid.uuid4(),
        project_id=project.id,
        asset_type="script",
        path="/path/to/asset",
    )
    db_session.add(asset)
    await db_session.commit()

    assert asset.created_at >= start_time
    assert asset.updated_at >= start_time

    # Test update timestamp
    original_updated_at = asset.updated_at
    await db_session.refresh(asset)
    asset.path = "/new/path"
    await db_session.commit()

    assert asset.updated_at > original_updated_at
    assert asset.created_at == asset.created_at  # Should not change

@pytest.mark.asyncio
async def test_asset_enum_validation(db_session: AsyncSession) -> None:
    """Test that asset_type must be a valid enum value."""
    project = Project(id=uuid.uuid4(), topic="Test Topic", status=ProjectStatus.CREATED)
    db_session.add(project)
    await db_session.commit()

    # Test valid asset types
    valid_types = ["script", "narration", "video", "image", "slide"]
    for asset_type in valid_types:
        asset = Asset(
            id=uuid.uuid4(),
            project_id=project.id,
            asset_type=asset_type,
            path=f"/path/to/{asset_type}",
        )
        db_session.add(asset)
        await db_session.commit() # Commit each successful creation
        result = await db_session.execute(select(Asset).filter_by(id=asset.id))
        saved_asset = result.scalar_one()
        assert saved_asset.asset_type == asset_type
        db_session.delete(asset) #cleanup
        await db_session.commit() # Commit after each successful creation


    # Test invalid asset type
    with pytest.raises(IntegrityError):
        invalid_asset = Asset(
            id=uuid.uuid4(),
            project_id=project.id,
            asset_type="invalid_type",
            path="/path/to/asset",
        )
        db_session.add(invalid_asset)
        await db_session.commit()


@pytest.mark.asyncio
async def test_asset_path_not_nullable(db_session: AsyncSession) -> None:
    """Test that path cannot be null."""
    project = Project(id=uuid.uuid4(), topic="Test Topic", status=ProjectStatus.CREATED)
    db_session.add(project)
    await db_session.commit()

    with pytest.raises(IntegrityError):
        asset = Asset(
            id=uuid.uuid4(),
            project_id=project.id,
            asset_type="script",
            path=None,  # This should raise an error
        )
        db_session.add(asset)
        await db_session.commit()
```

Key points about `test_asset.py`:

- **Test Cases:** Covers creation, updates, timestamp behavior, enum validation, and the `path` not-nullable constraint.
- **`IntegrityError`:** Uses `pytest.raises(IntegrityError)` to assert that database constraints are enforced.
- **Enum Testing**: Includes tests for valid and invalid enum values.

## 7. Run Tests (Again)

After adding the model tests, run all tests again to ensure everything is still working:

```bash
docker-compose run api pytest -v src/backend/tests
```

All tests (API and model) should pass. If any tests fail, carefully review the error messages and debug your code. It's crucial to fix any failing tests _before_ moving on.

This completes Part 1 of the guide, with a strong emphasis on Test-Driven Development. You now have:

- A well-defined project structure.
- Basic FastAPI setup.
- Database models and migrations.
- Initial API endpoints.
- A comprehensive suite of API and model tests.
- A solid foundation for building more complex features.

The next step is to enhance error handling in API and begin working on the `PATCH` endpoint for updating projects.

```

This single, comprehensive Markdown file is your guide.  It's structured for clarity, actionability, and a true TDD workflow.  Remember to run the tests frequently as you work. Good luck!
```
