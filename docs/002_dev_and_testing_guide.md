Repository Review (High-Level)

You've done an excellent job setting up the project structure, incorporating best practices, and addressing the initial feedback. Here's a summary of my observations:

Structure: The project structure is well-organized, separating frontend, backend, models, schemas, etc. This is crucial for maintainability and scalability. The use of src/backend and src/frontend is excellent.

Dependencies: Your requirements.txt includes a good selection of essential libraries. You've also included development dependencies for testing and linting, which is excellent.

Type Hinting: You're using type hints extensively and consistently, which is fantastic. This will significantly improve code quality and catch errors early. You are also now using the Mapped types from SQLAlchemy, which is correct.

Asynchronous Programming: You're using async and await correctly with FastAPI and SQLAlchemy.

Database: SQLAlchemy and Alembic are set up for database interactions and migrations. You have a good basic model defined (Project, Asset). The use of a separate test database is crucial for test isolation.

Configuration: You're using Pydantic's BaseSettings for managing configuration, which is a best practice. The use of .env files is correct.

Docker: Docker and Docker Compose are set up, which is essential for consistent development and deployment environments. Your Dockerfiles are well-structured, using multi-stage builds for the frontend and separate containers for the API, Celery worker, Postgres, and Redis.

Linting/Formatting: You've got mypy, flake8, black, and isort configured, and importantly, you've configured them to work together without conflicts. You've also added autoflake to remove unused imports. This is a very strong setup.

Pre-commit Hooks: You're using pre-commit hooks to automate linting and formatting. This is excellent for maintaining code quality.

Frontend (Next.js): The basic Next.js setup is in place, including routing, Clerk authentication, and shadcn/ui integration.

API Endpoints: You've got the basic CRUD endpoints for projects defined. You're using Pydantic schemas for request and response validation. You have basic error handling.

Celery: Celery is installed and configured.

Documentation: You are using markdown files to keep track of your progress, which is great.

Key Areas to Focus on Next (Testing & Beyond):

Testing (Immediate Priority): As you've identified, this is the most critical next step. You have the basic fixtures, now you need to write comprehensive test cases.

Error Handling (Enhancements): While you have some basic HTTPException handling, you'll need to expand this to be more robust, especially around database operations (e.g., handling connection errors, unique constraint violations). Use structured logging with your errors.

Celery Task Implementation: The process_project task is currently a placeholder. You'll need to implement the actual logic for generating video assets.

Frontend - Backend Communication: Get your Next.js frontend making API calls to your FastAPI backend.

Frontend UI: Build the UI to view and filter the projects.



Okay, let's continue building the consolidated development and testing guide. This part focuses on **Backend Testing and Error Handling**. We'll build on the previous overview, adding specific code examples and expanding on error handling.

```markdown
# Content Platform Development and Testing Guide

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
- [x] API Setup
  - [x] Basic FastAPI configuration
  - [x] /health endpoint
  - [x] CORS middleware
  - [x] Projects router
- [x] Authentication
  - [x] Clerk integration
  - [x] Environment variables for Clerk
- [x] Frontend Foundation
  - [x] Next.js setup with TypeScript
  - [x] Shadcn/ui integration
  - [x] Dark mode support
  - [x] Basic routing structure
- [x] Task Queue
  - [x] Celery basic setup
  - [x] Redis integration
  - [x] Test task implementation
- [x] Linting and Formatting
  - [x] mypy, flake8, black, isort, autoflake configuration
  - [x] pre-commit hooks setup

### In Progress 🚧

- [ ] **Testing Infrastructure**
  - [x] `conftest.py` setup
    - [x] Basic fixtures defined (`setup_database`, `db_session`, `client`)
    - [x] Test database configuration
    - [x] Database isolation per test (rollback after each test)
  - [ ] **API Tests** (`src/backend/tests/test_api/test_projects.py`)
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
    - [ ] `/projects/{id}` PATCH endpoint  *<-- Focus here next*
        - [ ] Basic field updates (topic, notes)
        - [ ] Status updates
        - [ ] Not found case
        - [ ] Invalid status value
        - [ ] Partial updates (only updating some fields)
        - [ ] Edge cases (empty strings, etc.)
        - [ ] Error case coverage
  - [ ] Model Tests
    - [x] Project model creation
    - [x] Project status transitions
    - [x] Project-Asset relationship
    - [x] Project cascade delete
    - [ ] Asset model *<-- Then model tests*
  - [ ] Task Tests *<-- Then task tests*
    - [ ] Celery configuration tests
    - [ ] Task execution tests
    - [ ] Task error handling

- [x] **Error Handling (Basic API)** *<-- We'll enhance this as we test*
  - [x] Database Operations (in `projects.py`)
    - [ ] Connection errors  *<-- Add specific connection error handling*
    - [x] Transaction errors (rollback on exception)
    - [ ] Constraint violations *<-- Add when you have constraints*
  - [x] API Endpoints
    - [x] Input validation (handled by Pydantic)
    - [x] Not found handling
    - [ ] Conflict handling *<-- Add when relevant (e.g., duplicate topics)*
  - [ ] Task Processing
    - [ ] Task failure handling
    - [ ] Retry logic
    - [ ] Status updates

- [ ] Logging System *<-- After basic error handling*
  - [x] JSON logging setup (done in `main.py`)
  - [x] Log levels configuration (INFO level is good for now)
  - [ ] Request logging (middleware) *<-- Add middleware for request logging*
  - [x] Error logging (done - enhance with more context)
  - [ ] Task logging *<-- Add when implementing tasks*

### Next Steps 📋

1.  **Complete API Tests (PATCH endpoint):** Focus on the `/projects/{id}` PATCH endpoint tests.
2.  **Enhance Error Handling:** Add specific database connection error handling and conflict handling.
3.  **Model Tests:** Complete tests for the `Asset` model.
4.  **Task Tests:** Write basic Celery configuration and task execution tests.
5. **Request Logging Middleware:** Implement a middleware to automatically log all requests.

## Part 1: Comprehensive Backend Testing (Continued)

### Step 1.1:  `/projects/{id}` PATCH Endpoint Tests

We'll expand `src/backend/tests/test_api/test_projects.py` to include tests for the update (PATCH) endpoint.  This is where we'll focus on the cases outlined above.

```python
# src/backend/tests/test_api/test_projects.py (Complete File - Including Previous Tests)
import pytest
from httpx import AsyncClient
from uuid import uuid4, UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.backend.schemas.project import ProjectCreate, ProjectStatus, ProjectUpdate
from src.backend.models.project import Project
from sqlalchemy import select
from fastapi import status  # Import for status codes


@pytest.mark.asyncio
async def test_create_project(client: AsyncClient, db_session: AsyncSession):
    # ... (Existing test_create_project - No changes needed here) ...
    """Test successful project creation"""
    data = ProjectCreate(topic="Test Topic", notes="Test Notes", name="Test Name").model_dump()
    response = await client.post("/api/v1/projects/", json=data)

    assert response.status_code == status.HTTP_201_CREATED
    project_dict = response.json()
    assert project_dict["topic"] == "Test Topic"
    assert project_dict["notes"] == "Test Notes"
    assert project_dict["name"] == "Test Name"
    assert project_dict["status"] == ProjectStatus.CREATED.value
    assert "id" in project_dict
    assert isinstance(UUID(project_dict["id"]), UUID)

    # Check if the project exists in the database
    retrieved_project = await db_session.get(Project, UUID(project_dict["id"]))
    assert retrieved_project is not None
    assert retrieved_project.topic == "Test Topic"
    assert retrieved_project.name == "Test Name"


@pytest.mark.asyncio
async def test_create_project_missing_topic(client: AsyncClient):
    # ... (Existing test_create_project_missing_topic - No changes needed) ...
    """Test project creation with missing required field"""
    data: dict[str, str] = {"notes": "Test Notes"}
    response = await client.post("/api/v1/projects/", json=data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_project_invalid_topic(client: AsyncClient):
    # ... (Existing test_create_project_invalid_topic - No changes needed) ...
    """Test project creation with invalid topic type (e.g., number instead of string)"""
    data: dict[str, str | int] = {"topic": 123, "notes": "Test Notes"}  # Invalid topic type
    response = await client.post("/projects/", json=data)
    assert response.status_code == 422  # Expecting a validation error

@pytest.mark.asyncio
async def test_get_project_status(client: AsyncClient, db_session: AsyncSession):
    # ... (Existing test_get_project_status - No changes needed) ...
    """Test getting project status"""
    # Create a project first
    project = Project(
        id=uuid4(), topic="Test Topic", notes="Test Notes", status=ProjectStatus.CREATED
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    # Get its status
    status_response = await client.get(f"/projects/{project.id}/status")
    assert status_response.status_code == 200
    status = status_response.json()
    assert status["status"] == "CREATED"

@pytest.mark.asyncio
async def test_get_project_status_not_found(client: AsyncClient):
    # ... (Existing test_get_project_status_not_found - No changes needed) ...
    """Test getting status of non-existent project"""
    non_existent_id = str(uuid4())
    response = await client.get(f"/projects/{non_existent_id}/status")
    assert response.status_code == 404
    assert response.json() == {"detail": "Project not found"}

@pytest.mark.asyncio
async def test_get_project(client: AsyncClient, db_session: AsyncSession):
    # ... (Existing test_get_project - No changes needed) ...
    """Test getting a project by ID"""
    # Create a project first
    project = Project(topic="Test Topic", notes="Test Notes", status="CREATED")
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    # Get the project
    get_response = await client.get(f"/projects/{project.id}")
    assert get_response.status_code == 200
    project_data = get_response.json()
    assert project_data["id"] == str(project.id)
    assert project_data["topic"] == "Test Topic"
    assert project_data["notes"] == "Test Notes"
    assert project_data["status"] == "CREATED"

@pytest.mark.asyncio
async def test_get_project_not_found(client: AsyncClient):
    # ... (Existing test_get_project_not_found - No changes needed) ...
    """Test getting a non-existent project by ID"""
    non_existent_id = str(uuid4())
    response = await client.get(f"/projects/{non_existent_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Project not found"}

@pytest.mark.asyncio
async def test_get_project_invalid_id(client: AsyncClient):
    # ... (Existing test_get_project_invalid_id - No changes needed) ...
    """Test getting a project with an invalid ID format"""
    invalid_id = "not-a-uuid"
    response = await client.get(f"/projects/{invalid_id}")
    assert response.status_code == 422  # Expecting a validation error

@pytest.mark.asyncio
async def test_list_projects(client: AsyncClient, db_session: AsyncSession):
    # ... (Existing test_list_projects - No changes needed) ...
    """Test getting a list of projects"""
    # Create a few projects
    project1 = Project(
        id=uuid4(), topic="Topic 1", notes="Notes 1", status=ProjectStatus.CREATED
    )
    project2 = Project(
        id=uuid4(), topic="Topic 2", notes="Notes 2", status=ProjectStatus.PROCESSING
    )
    db_session.add_all([project1, project2])
    await db_session.commit()

    # Get the list of projects
    response = await client.get("/projects/")
    assert response.status_code == 200
    projects_list: list[dict[str, str]] = response.json()
    assert isinstance(projects_list, list)
    assert len(projects_list) == 2

    # Check if the projects have expected data (optional, but good practice)
    topics: set[str] = {str(p["topic"]) for p in projects_list}
    assert "Topic 1" in topics
    assert "Topic 2" in topics

@pytest.mark.asyncio
async def test_update_project(client: AsyncClient, db_session: AsyncSession):
    """Test updating a project's fields"""
    # Create initial project
    project = Project(
        topic="Original Topic", notes="Original Notes", status=ProjectStatus.CREATED
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    # Update the project
    update_data = {"topic": "Updated Topic", "notes": "Updated Notes"}
    response = await client.patch(f"/api/v1/projects/{project.id}", json=update_data)

    assert response.status_code == 200
    updated_project = response.json()
    assert updated_project["topic"] == "Updated Topic"
    assert updated_project["notes"] == "Updated Notes"
    assert updated_project["status"] == "CREATED"  # Status should remain unchanged

    # Verify in database
    retrieved_project = await db_session.get(Project, project.id)
    assert retrieved_project.topic == "Updated Topic"
    assert retrieved_project.notes == "Updated Notes"

@pytest.mark.asyncio
async def test_update_project_status(client: AsyncClient, db_session: AsyncSession):
    """Test updating a project's status"""
    project = Project(topic="Status Update Test", status=ProjectStatus.CREATED)
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    # Update to PROCESSING
    update_data = {"status": "PROCESSING"}
    response = await client.patch(f"/api/v1/projects/{project.id}", json=update_data)

    assert response.status_code == 200
    updated_project = response.json()
    assert updated_project["status"] == "PROCESSING"

      # Verify in database
    retrieved_project = await db_session.get(Project, project.id)
    assert retrieved_project.status == ProjectStatus.PROCESSING


    # Update to COMPLETED
    update_data = {"status": "COMPLETED"}
    response = await client.patch(f"/api/v1/projects/{project.id}", json=update_data)

    assert response.status_code == 200
    updated_project = response.json()
    assert updated_project["status"] == "COMPLETED"

     # Verify in database
    retrieved_project = await db_session.get(Project, project.id)
    assert retrieved_project.status == ProjectStatus.COMPLETED

@pytest.mark.asyncio
async def test_update_project_not_found(client: AsyncClient):
    """Test updating a non-existent project"""
    non_existent_id = str(uuid4())
    update_data = {"topic": "New Topic"}
    response = await client.patch(f"/api/v1/projects/{non_existent_id}", json=update_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "Project not found"}


@pytest.mark.asyncio
async def test_update_project_invalid_status(client: AsyncClient, db_session: AsyncSession):
    """Test updating a project with an invalid status (through API)"""
    project = Project(topic="Invalid Status Test", status=ProjectStatus.CREATED)
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    # Try to update with invalid status
    update_data = {"status": "INVALID_STATUS"}  # Invalid status
    response = await client.patch(f"/api/v1/projects/{project.id}", json=update_data)

    assert response.status_code == 422  # Expect a validation error

@pytest.mark.asyncio
async def test_update_project_partial_update(client: AsyncClient, db_session: AsyncSession):
    """Test updating only some fields of a project."""
    project = Project(topic="Original Topic", notes="Original Notes", status=ProjectStatus.CREATED)
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    update_data = {"topic": "New Topic"}  # Only update the topic
    response = await client.patch(f"/api/v1/projects/{project.id}", json=update_data)
    assert response.status_code == 200
    updated_project = response.json()
    assert updated_project["topic"] == "New Topic"
    assert updated_project["notes"] == "Original Notes"  # Notes should be unchanged
    assert updated_project["status"] == "CREATED" # Status should be unchanged

    #Verify in the database
    retrieved_project = await db_session.get(Project, project.id)
    assert retrieved_project.topic == "New Topic"
    assert retrieved_project.notes == "Original Notes"


@pytest.mark.asyncio
async def test_update_project_empty_topic(client: AsyncClient, db_session: AsyncSession):
    """Test updating a project with an empty topic (edge case)."""
    project = Project(topic="Original Topic", notes="Notes", status=ProjectStatus.CREATED)
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    update_data = {"topic": ""}  # Empty string for topic
    response = await client.patch(f"/api/v1/projects/{project.id}", json=update_data)
    assert response.status_code == 422 #Should fail the validation

@pytest.mark.asyncio
async def test_update_project_empty_notes(client: AsyncClient, db_session: AsyncSession):
    """Test updating a project with empty notes (allowed, optional field)."""
    project = Project(topic="Original Topic", notes="Notes", status=ProjectStatus.CREATED)
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    update_data = {"notes": ""}  # Empty notes
    response = await client.patch(f"/api/v1/projects/{project.id}", json=update_data)
    assert response.status_code == 200
    updated_project = response.json()
    assert updated_project["notes"] == ""

    # Verify in the database.
    retrieved_project = await db_session.get(Project, project.id)
    assert retrieved_project is not None
    assert retrieved_project.notes == "" # Should be updated

@pytest.mark.asyncio
async def test_update_project_null_notes(client: AsyncClient, db_session: AsyncSession):
    """Test setting notes to null"""
    project = Project(topic="Original Topic", notes="Notes", status=ProjectStatus.CREATED)
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    update_data = {"notes": None} #Explicit None
    response = await client.patch(f"/api/v1/projects/{project.id}", json=update_data)
    assert response.status_code == 200
    updated_project = response.json()
    assert updated_project["notes"] is None

    # Verify in the database.
    retrieved_project = await db_session.get(Project, project.id)
    assert retrieved_project is not None
    assert retrieved_project.notes is None
```

Key Additions and Explanations:

*   **`test_update_project_partial_update`:**  This is crucial.  It verifies that you can update *only* specific fields without affecting others.  This is the core behavior of a PATCH request.
*   **`test_update_project_empty_topic`:**  Tests the edge case of sending an empty string for a required field.  This *should* fail validation (Pydantic will handle this).
*   **`test_update_project_empty_notes`:** Tests sending an empty string for an *optional* field.  This should be allowed and should update the field to an empty string.
*  **`test_update_project_null_notes`:** Test setting an optional field to null.
*   **`status.HTTP_201_CREATED`:** Uses the named constant for clarity and consistency.
*   **Database Assertions:** Added more direct database assertions in all update tests.

**Running the Tests:**

```bash
docker-compose run api pytest -v src/backend/tests/test_api/test_projects.py
```

### Step 1.2: Enhance Error Handling in `projects.py`

Now, let's improve the error handling in your API endpoints, specifically within `src/backend/api/routers/projects.py`.

```python
# src/backend/api/routers/projects.py
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import OperationalError  # Import OperationalError

from src.backend.core.database import get_db
from src.backend.models.project import Project
from src.backend.schemas.project import (
    ProjectCreate,
    ProjectRead,
    ProjectStatus,
    ProjectUpdate,
)
from src.backend.core.config import settings #For easy settings access
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate, db: AsyncSession = Depends(get_db)
) -> ProjectRead:
    try:
        db_project = Project(
            id=uuid.uuid4(),
            topic=project.topic,
            name=project.name,
            notes=project.notes,
            status=ProjectStatus.CREATED,
        )
        db.add(db_project)
        await db.commit()
        await db.refresh(db_project)
        return ProjectRead.model_validate(db_project)
    except OperationalError as e:  # Catch database connection errors
        await db.rollback()
        logger.error(f"Database operational error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Database connection error")
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating project: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{project_id}/status", response_model=ProjectStatus)
async def get_status(
    project_id: str, db: AsyncSession = Depends(get_db)
) -> ProjectStatus:
    try:
        result = await db.execute(select(Project).filter(Project.id == project_id))
        db_project = result.scalar_one_or_none()
        if not db_project:
            raise HTTPException(status_code=404, detail="Project not found")
        return db_project.status
    except OperationalError as e:
        logger.error(f"Database operational error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Database connection error")
    except Exception as e:
        logger.error(f"Error getting project status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")



@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(
    project_id: str, db: AsyncSession = Depends(get_db)
) -> ProjectRead:
    try:
        result = await db.execute(select(Project).filter(Project.id == project_id))
        db_project = result.scalar_one_or_none()
        if not db_project:
            raise HTTPException(status_code=404, detail="Project not found")
        return ProjectRead.model_validate(db_project)
    except OperationalError as e:
        logger.error(f"Database operational error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Database connection error")
    except Exception as e:
        logger.error(f"Error getting project: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/", response_model=List[ProjectRead])
async def list_projects(db: AsyncSession = Depends(get_db)) -> List[ProjectRead]:
    try:
        result = await db.execute(select(Project))
        projects = result.scalars().all()
        return [ProjectRead.model_validate(p) for p in projects]
    except OperationalError as e:
        logger.error(f"Database operational error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Database connection error")
    except Exception as e:
        logger.error(f"Error listing projects: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.patch("/{project_id}", response_model=ProjectRead)
async def update_project(project_id: str, project_update: ProjectUpdate, db: AsyncSession = Depends(get_db)):

    try:
        result = await db.execute(select(Project).filter(Project.id == project_id))
        project = result.scalar_one_or_none()
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")

        update_data = project_update.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(project, key, value)

        db.add(project)  # Make sure the project is added to the session
        await db.commit()
        await db.refresh(project)
        return project
    except OperationalError as e:
        await db.rollback()
        logger.error(f"Database operational error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Database connection error")
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating project: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

```

Key Changes and Explanations:

*   **`OperationalError`:**  We specifically catch `sqlalchemy.exc.OperationalError`.  This exception is raised for database connection problems, which is a critical thing to handle gracefully.
*   **Database Connection Error Handling:** In the `except OperationalError` block, we now:
    *   Log the error using `logger.error`, including the exception details (`exc_info=True` gives you the stack trace).
    *   Raise an `HTTPException` with a `500` status code and a user-friendly message ("Database connection error").  Don't expose internal error details to the client.
*  **Consistent Error Handling**: Added similar error handling to all of the api endpoint functions.
* **Type Consistency**: Ensured consistent type hints and return types.

**Testing the Error Handling:**

You *cannot* easily test the `OperationalError` handling with your current `httpx.AsyncClient` setup.  `AsyncClient` directly interacts with your FastAPI application, which, during tests, is connected to an *in-memory* test database.  You won't get a real database connection error unless the database server itself is down (which you don't want to simulate in unit/integration tests).

To test database connection errors, you'd typically need to do one of the following:

1.  **Mocking (Advanced):** Use a library like `unittest.mock` (or `pytest-mock`, which is a nice wrapper around `unittest.mock`) to *mock* the database connection and force it to raise an `OperationalError`.  This is a more advanced technique, but it's the most reliable way to test this specific error handling in isolation.
2.  **Integration/System Tests (Separate Suite):** Create a separate suite of tests that run against a *real* (but still disposable) PostgreSQL database.  In these tests, you could temporarily shut down the database to simulate a connection error.  This is more complex to set up, but it tests the entire system end-to-end.

For now, since you're focusing on solidifying v0.0, I recommend focusing on the tests you *can* easily write with your current setup (the API endpoint logic, validation, etc.).  You can add more advanced error handling tests later.  The important thing is that you have the `try...except` blocks in place, and you're logging the errors.

### Step 1.3: Model Tests (Asset Model)

Create `src/backend/tests/test_models/test_asset.py`:

```python
# src/backend/tests/test_models/test_asset.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.backend.models.asset import Asset
from src.backend.models.project import Project
from src.backend.schemas.project import ProjectStatus
import uuid
from datetime import datetime, timezone
import asyncio  # Import asyncio
import sqlalchemy.exc  # Import sqlalchemy.exc


@pytest.mark.asyncio
async def test_create_asset(db_session: AsyncSession):
    """Test creating an Asset."""

    # You need a Project to associate the Asset with
    project = Project(id=uuid.uuid4(), topic="Test Topic", name="Test Project", status=ProjectStatus.CREATED)
    db_session.add(project)
    await db_session.commit() #Commit to get the ID
    await db_session.refresh(project) #Refresh to use in the asset


    asset = Asset(
        id=uuid.uuid4(),
        project_id=project.id,
        asset_type="script",
        path="/path/to/script",
        approved=True
    )
    db_session.add(asset)
    await db_session.commit()

    result = await db_session.execute(select(Asset).filter_by(id=asset.id))
    saved_asset = result.scalar_one()

    assert saved_asset.project_id == project.id
    assert saved_asset.asset_type == "script"
    assert saved_asset.path == "/path/to/script"
    assert saved_asset.approved is True
    assert saved_asset.created_at is not None
    assert saved_asset.updated_at is not None
    assert saved_asset.created_at <= saved_asset.updated_at

@pytest.mark.asyncio
async def test_asset_update(db_session: AsyncSession):
    """Test updating an Asset."""
    project = Project(id=uuid.uuid4(), topic="Test Topic", name="Test Project", status=ProjectStatus.CREATED)
    db_session.add(project)
    await db_session.commit() #Commit to get the ID
    await db_session.refresh(project) #Refresh to use in the asset

    asset = Asset(
        id=uuid.uuid4(),
        project_id=project.id,
        asset_type="script",
        path="/path/to/script",
    )
    db_session.add(asset)
    await db_session.commit()
    await db_session.refresh(asset)

    updated_path = "/new/path/to/script"
    asset.path = updated_path
    asset.approved = True
    await db_session.commit()

    result = await db_session.execute(select(Asset).filter_by(id=asset.id))
    updated_asset = result.scalar_one()
    assert updated_asset.path == updated_path
    assert updated_asset.approved is True
    assert updated_asset.updated_at >= updated_asset.created_at

@pytest.mark.asyncio
async def test_asset_timestamp_update(db_session: AsyncSession):
    """Test that updated_at is updated."""
    project = Project(id=uuid.uuid4(), topic="Test Topic", name="Test Project", status=ProjectStatus.CREATED)
    db_session.add(project)
    await db_session.commit() #Commit to get the ID
    await db_session.refresh(project) #Refresh to use in the asset
    asset = Asset(
        id=uuid.uuid4(),
        project_id=project.id,
        asset_type="script",
        path="/path/to/script",
    )
    db_session.add(asset)
    await db_session.commit()
    await db_session.refresh(asset)

    original_updated_at = asset.updated_at
    # Wait slightly to ensure a time difference.  In real-world tests, you might need to use
    # `freezegun` or similar to control the system clock for precise timestamp testing.
    # For this example, a small delay is sufficient.
    await asyncio.sleep(0.01)  # Use asyncio.sleep with await

    asset.path = "/new/path/to/script"
    await db_session.commit()
    await db_session.refresh(asset)
    assert asset.updated_at > original_updated_at

@pytest.mark.asyncio
async def test_asset_type_enum(db_session: AsyncSession):
    """Test the asset_type Enum constraint."""
    project = Project(id=uuid.uuid4(), topic="Test Topic", name="Test Project", status=ProjectStatus.CREATED)
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    # Test valid values
    valid_types = ["script", "narration", "video", "image", "slide"]
    for asset_type in valid_types:
        asset = Asset(id=uuid.uuid4(), project_id=project.id, asset_type=asset_type, path="/path/to/asset")
        db_session.add(asset)
        await db_session.commit()
        await db_session.delete(asset) #Clean up after each valid type test
        await db_session.commit()

    #Test invalid values.  This requires catching the expected exception.
    with pytest.raises(Exception) as e:  # Catch *any* exception, since DB type varies
        asset = Asset(id=uuid.uuid4(), project_id=project.id, asset_type="invalid_type", path="/path/to/asset")
        db_session.add(asset)
        await db_session.commit()  # This should raise an exception
    assert e.type is not None  # Check that an exception was actually raised. More specific check below

    #More precise check depending on the database.
    #The raised exception will be different between database systems.
    #The best way is with a generic Exception, as shown above.
    #You should use the method above, and these are included below just as an example.
    # if settings.DATABASE_URL.startswith("postgresql"):
    #    assert isinstance(e.value, (sqlalchemy.exc.StatementError, psycopg2.errors.InvalidTextRepresentation))
    # elif settings.DATABASE_URL.startswith("sqlite"):
    #     assert isinstance(e.value, sqlite3.IntegrityError)

    await db_session.rollback() #Rollback to avoid the invalid state

@pytest.mark.asyncio
async def test_asset_path_not_nullable(db_session: AsyncSession):
    """Test that the path field cannot be null."""
    project = Project(id=uuid.uuid4(), topic="Test Topic", name="Test Project", status=ProjectStatus.CREATED)
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    with pytest.raises(Exception) as excinfo:  # Catch *any* exception
        asset = Asset(id=uuid.uuid4(), project_id=project.id, asset_type="script", path=None) # type: ignore
        db_session.add(asset)
        await db_session.commit()
    assert excinfo.type is not None
    await db_session.rollback()

```python


Let's continue building out the `test_asset.py` file and then move on to Celery task testing.

# src/backend/tests/test_models/test_asset.py (Complete File)
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.backend.models.asset import Asset
from src.backend.models.project import Project
from src.backend.schemas.project import ProjectStatus  # Import ProjectStatus
import uuid
from datetime import datetime, timezone
import asyncio  # Import asyncio


@pytest.mark.asyncio
async def test_create_asset(db_session: AsyncSession):
    """Test creating an Asset."""

    # You need a Project to associate the Asset with
    project = Project(id=uuid.uuid4(), topic="Test Topic", name="Test Project", status=ProjectStatus.CREATED)
    db_session.add(project)
    await db_session.commit() #Commit to get the ID
    await db_session.refresh(project) #Refresh to use in the asset


    asset = Asset(
        id=uuid.uuid4(),
        project_id=project.id,
        asset_type="script",
        path="/path/to/script",
        approved=True
    )
    db_session.add(asset)
    await db_session.commit()

    result = await db_session.execute(select(Asset).filter_by(id=asset.id))
    saved_asset = result.scalar_one()

    assert saved_asset.project_id == project.id
    assert saved_asset.asset_type == "script"
    assert saved_asset.path == "/path/to/script"
    assert saved_asset.approved is True
    assert saved_asset.created_at is not None
    assert saved_asset.updated_at is not None
    assert saved_asset.created_at <= saved_asset.updated_at

@pytest.mark.asyncio
async def test_asset_update(db_session: AsyncSession):
    """Test updating an Asset."""
    project = Project(id=uuid.uuid4(), topic="Test Topic", name="Test Project", status=ProjectStatus.CREATED)
    db_session.add(project)
    await db_session.commit() #Commit to get the ID
    await db_session.refresh(project) #Refresh to use in the asset

    asset = Asset(
        id=uuid.uuid4(),
        project_id=project.id,
        asset_type="script",
        path="/path/to/script",
    )
    db_session.add(asset)
    await db_session.commit()
    await db_session.refresh(asset)

    updated_path = "/new/path/to/script"
    asset.path = updated_path
    asset.approved = True
    await db_session.commit()

    result = await db_session.execute(select(Asset).filter_by(id=asset.id))
    updated_asset = result.scalar_one()
    assert updated_asset.path == updated_path
    assert updated_asset.approved is True
    assert updated_asset.updated_at >= updated_asset.created_at

@pytest.mark.asyncio
async def test_asset_timestamp_update(db_session: AsyncSession):
    """Test that updated_at is updated."""
    project = Project(id=uuid.uuid4(), topic="Test Topic", name="Test Project", status=ProjectStatus.CREATED)
    db_session.add(project)
    await db_session.commit() #Commit to get the ID
    await db_session.refresh(project) #Refresh to use in the asset
    asset = Asset(
        id=uuid.uuid4(),
        project_id=project.id,
        asset_type="script",
        path="/path/to/script",
    )
    db_session.add(asset)
    await db_session.commit()
    await db_session.refresh(asset)

    original_updated_at = asset.updated_at
    # Wait slightly to ensure a time difference.  In real-world tests, you might need to use
    # `freezegun` or similar to control the system clock for precise timestamp testing.
    # For this example, a small delay is sufficient.
    await asyncio.sleep(0.01)  # Use asyncio.sleep with await

    asset.path = "/new/path/to/script"
    await db_session.commit()
    await db_session.refresh(asset)
    assert asset.updated_at > original_updated_at

@pytest.mark.asyncio
async def test_asset_type_enum(db_session: AsyncSession):
    """Test the asset_type Enum constraint."""
    project = Project(id=uuid.uuid4(), topic="Test Topic", name="Test Project", status=ProjectStatus.CREATED)
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    # Test valid values
    valid_types = ["script", "narration", "video", "image", "slide"]
    for asset_type in valid_types:
        asset = Asset(id=uuid.uuid4(), project_id=project.id, asset_type=asset_type, path="/path/to/asset")
        db_session.add(asset)
        await db_session.commit()
        await db_session.delete(asset) #Clean up after each valid type test
        await db_session.commit()

    #Test invalid values.  This requires catching the expected exception.
    with pytest.raises(Exception) as e:  # Catch *any* exception, since DB type varies
        asset = Asset(id=uuid.uuid4(), project_id=project.id, asset_type="invalid_type", path="/path/to/asset")
        db_session.add(asset)
        await db_session.commit()  # This should raise an exception
    assert e.type is not None  # Check that an exception was actually raised. More specific check below

    #More precise check depending on the database.
    #The raised exception will be different between database systems.
    #The best way is with a generic Exception, as shown above.
    #You should use the method above, and these are included below just as an example.
    # if settings.DATABASE_URL.startswith("postgresql"):
    #    assert isinstance(e.value, (sqlalchemy.exc.StatementError, psycopg2.errors.InvalidTextRepresentation))
    # elif settings.DATABASE_URL.startswith("sqlite"):
    #     assert isinstance(e.value, sqlite3.IntegrityError)

    await db_session.rollback() #Rollback to avoid the invalid state

@pytest.mark.asyncio
async def test_asset_path_not_nullable(db_session: AsyncSession):
    """Test that the path field cannot be null."""
    project = Project(id=uuid.uuid4(), topic="Test Topic", name="Test Project", status=ProjectStatus.CREATED)
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    with pytest.raises(Exception) as excinfo:  # Catch *any* exception
        asset = Asset(id=uuid.uuid4(), project_id=project.id, asset_type="script", path=None) # type: ignore
        db_session.add(asset)
        await db_session.commit()
    assert excinfo.type is not None
    await db_session.rollback()

```

Key additions and explanations for `test_asset.py`:

*   **`test_asset_type_enum`:** This test is *critical*. It verifies that your database's `ENUM` constraint for `asset_type` is working correctly.  It does this by:
    *   Testing all *valid* enum values to ensure they are accepted.
    *   Attempting to create an `Asset` with an *invalid* enum value. We expect this to raise an exception.  We use `pytest.raises(Exception)` as a context manager to assert that an exception *is* raised.  The specific exception type might vary depending on your database (PostgreSQL, SQLite, etc.), so we catch the base `Exception` class.  You could be more specific if you know the exact exception type your database will raise (see the commented-out example).  Critically, we roll back the transaction after the expected error.
*   **`test_asset_path_not_nullable`:** This test confirms that the `path` field, which is defined as `nullable=False` in your model, actually enforces that constraint at the database level.
*   **`test_asset_update`:** Tests updating fields on the Asset model.
*   **`test_asset_timestamp_update`:**  This is a good test to ensure that the `updated_at` field is automatically updated when the model changes.  Because timestamps can be tricky (due to database precision and timing), we add a small delay using `asyncio.sleep(0.01)`.  This gives the database time to update the timestamp.
*   **Docstrings:** Added docstrings to explain each test.
*   **Type Hints:**  Consistent type hints.
* **Imports**: Added any missing imports.
* **Project Creation**: Creates a project in setup, before creating an asset.

**Running the Model Tests:**

```bash
docker-compose run api pytest -v src/backend/tests/test_models
```

### Step 1.4: Celery Task Tests

Create `src/backend/tests/test_tasks/test_project_tasks.py`:

```python
# src/backend/tests/test_tasks/test_project_tasks.py
import pytest
from src.backend.tasks.project_tasks import celery, test_task, process_project
from celery.result import AsyncResult

@pytest.fixture(scope="session")
def celery_config():
    return {
        'broker_url': 'memory://',  # Use in-memory broker for testing
        'result_backend': 'rpc://', #Use RPC result backend for testing.
        'task_always_eager': True,  # Run tasks synchronously
        'task_eager_propagates': True,
    }

@pytest.mark.celery
def test_test_task(celery_app):
    result = test_task.delay(2, 3)
    assert result.get() == 5
    assert result.successful()

@pytest.mark.celery
def test_process_project_task(celery_app):
    #For now, this will just check that the task runs without error.
    #As you implement project processing steps, you can add assertions
    #to verify the behavior.
    result = process_project.delay("a-fake-project-id")
    assert result.successful()
    # TODO: Add assertions about database state changes, etc.
    #       once you implement the task logic.

# Example of testing a task failure (when you have error handling)
# @pytest.mark.celery
# def test_process_project_task_failure(celery_app):
#     with pytest.raises(Exception):  # Replace with your expected exception
#         result = failing_task.delay()
#         result.get()  # This will raise the exception if the task failed
#     assert result.failed()

```

Key points:

*   **`celery_config` fixture:**  This fixture is *crucial* for testing Celery.
    *   `broker_url = 'memory://'`:  Uses an in-memory broker for testing.  This is fast and avoids needing a real Redis instance.
    *   `result_backend = 'rpc://'`: Uses the RPC result backend. This allows you to get the return values of your tasks synchronously in your tests (using `result.get()`).
    *   `task_always_eager = True`:  This is *essential* for testing. It makes Celery tasks run *synchronously*, as if they were regular function calls.  This avoids all the complexities of asynchronous task execution during testing.  You *must* set this to `False` in your production `celeryconfig.py`.
    *   `task_eager_propagates = True`: Ensures that exceptions in tasks are propagated to the test, causing the test to fail (which is what you want).

*   **`@pytest.mark.celery`:**  Use this marker to indicate tests that require the Celery app.

*   **`test_test_task`:**  A very simple test to verify that Celery is configured correctly and can run a basic task.

*   **`test_process_project_task`:**  This is a placeholder for your `process_project` task tests.  Right now, it just checks that the task runs without errors.  As you implement the actual logic of `process_project`, you'll add assertions here to verify that the task does what it's supposed to do (e.g., creates database records, updates statuses, calls external APIs).

*   **Commented-out `test_process_project_task_failure`:** This is an *example* of how you would test a task that's designed to fail.  You'd use `pytest.raises` to assert that a specific exception is raised. You'll need to adapt this to your actual error handling logic.

**Running the Celery Tests:**

```bash
docker-compose run api pytest -v src/backend/tests/test_tasks
```

This completes the initial backend testing setup.  You now have:

*   Comprehensive API tests for your `/projects` endpoints, including the PATCH endpoint and error cases.
*   Robust model tests for both `Project` and `Asset` models.
*   A basic Celery testing setup with an example task test.
*  Improved error handling.

The next steps, as outlined in the guide, are to add more sophisticated error handling (connection errors, etc.), implement request logging middleware, and start connecting your frontend.  We'll continue to integrate testing as we add new features.

```

Excellent! You've made great progress. Now run the tests and make sure everything is passing before moving on. Let me know if you run into any issues, or when you're ready for the next section.
