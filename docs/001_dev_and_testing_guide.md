# Content Platform Development Guide - Part 1: Project Setup and Initial API/Model Tests

This is Part 1 of 4 in the Content Platform Development Guide series:

- Part 1 (Current): Project Setup and Initial API/Model Tests
- Part 2: PATCH Endpoint and Error Handling
- Part 3: Task Testing and Request Logging
- Part 4: Task Error Handling and Frontend Integration

This Part: Project Setup and Initial API/Model Tests

This part focuses on getting the basic project structure, API endpoints (create, get, list), and corresponding model and API tests in place.

This is one part of a multi-part guide to developing and testing the Content Platform. This part focuses on setting up the core project structure, defining the basic `Project` and `Asset` models, creating initial API endpoints for creating, retrieving, and listing projects, and writing tests for these endpoints and models.

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

### In Progress 🚧

- [ ] Initial Model Tests
  - [ ] Project model creation
  - [ ] Project status transitions
  - [ ] Project-Asset relationship
  - [ ] Project cascade delete
  - [ ] Asset model creation
  - [ ] Asset model updates
  - [ ] Asset model timestamp updates
  - [ ] Asset model enum validation
  - [ ] Asset model path not nullable
- [ ] Basic Error Handling
  - [ ] Initial try/except blocks in endpoints
  - [ ] Basic validation error responses

### Next Steps 📋

1. **Complete Basic Error Handling:** Add initial error handling to endpoints
2. **Move to PATCH Implementation:** Begin work on update functionality
3. **Document Initial API:** Document the basic endpoints

## 1. Project Structure (Review)

Make sure your project structure matches the following. You should have all these files and directories already. This is just a checklist.
content_copy
download
Use code with caution.
Markdown

alpha-w0lf-content_platform/
├── .docker/
│ ├── Dockerfile.api
│ ├── Dockerfile.celery
│ └── Dockerfile.frontend
├── src/
│ ├── backend/
│ │ ├── init.py
│ │ ├── alembic.ini
│ │ ├── celeryconfig.py
│ │ ├── main.py
│ │ ├── requirements.txt
│ │ ├── start.sh
│ │ ├── api/
│ │ │ ├── init.py
│ │ │ ├── dependencies.py
│ │ │ └── routers/
│ │ │ ├── init.py
│ │ │ └── projects.py
│ │ ├── core/
│ │ │ ├── init.py
│ │ │ ├── config.py
│ │ │ ├── database.py
│ │ │ └── utils.py
│ │ ├── migrations/
│ │ │ ├── init.py
│ │ │ ├── env.py
│ │ │ ├── script.py.mako
│ │ │ └── versions/
│ │ │ └── ... (your migration files)
│ │ ├── models/
│ │ │ ├── init.py
│ │ │ ├── asset.py
│ │ │ ├── base.py
│ │ │ └── project.py
│ │ ├── modules/
│ │ │ └── init.py
│ │ ├── prompts/
│ │ │ └── init.py
│ │ ├── schemas/
│ │ │ ├── init.py
│ │ │ ├── asset.py
│ │ │ └── project.py
│ │ ├── tasks/
│ │ │ ├── init.py
│ │ │ └── project_tasks.py
│ │ └── tests/
│ │ ├── init.py
│ │ ├── conftest.py
│ │ ├── test_api/
│ │ │ ├── init.py
│ │ │ └── test_projects.py
│ │ ├── test_models/
│ │ │ ├── init.py
│ │ │ ├── test_project.py
│ │ │ └── test_asset.py <-- NEW
│ │ └── test_modules/
│ │ └── init.py
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

## 2. Backend Code (Review and Ensure Consistency)

Review the following files and ensure they are consistent with the code provided in previous responses. Pay close attention to:

- **Type Hints:** Make sure all functions and methods have type hints.
- **Docstrings:** Make sure all functions and classes have docstrings explaining their purpose.
- **Error Handling:** Basic `try...except` blocks in API endpoints.
- **Imports**: Ensure all imports are present and organized.

- `src/backend/main.py`
- `src/backend/api/routers/projects.py`
- `src/backend/api/dependencies.py`
- `src/backend/core/config.py`
- `src/backend/core/database.py`
- `src/backend/core/utils.py`
- `src/backend/models/project.py`
- `src/backend/models/asset.py`
- `src/backend/models/__init__.py`
- `src/backend/schemas/project.py`
- `src/backend/schemas/asset.py`
- `src/backend/schemas/__init__.py`
- `src/backend/celeryconfig.py`
- `src/backend/migrations/env.py` (Make sure this is configured for asyncpg and your models)

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
content_copy
download
Use code with caution.

Key Points:

TEST_DATABASE_URL: Make sure this is correctly configured in your .env and config.py.

scope="function": Using function scope for setup_database and db_session ensures that each test function gets a fresh database and session, and that any changes are rolled back after the test. This is crucial for test isolation.

rollback(): The await session.rollback() in db_session is essential. It ensures that any changes made during a test are undone, preventing data from one test from affecting another.

app.dependency_overrides: Dependency overrides are cleared after the test.

4. Initial API Tests (test_projects.py) - Review

Review your src/backend/tests/test_api/test_projects.py file. It should include tests for the POST /projects/, GET /projects/{id}, GET /projects/{id}/status and GET /projects/ endpoints. It should be consistent with the complete file provided in previous responses, including all the tests for success, missing data, invalid data, and not found cases.

5. Initial Model Tests - Review

Review your src/backend/tests/test_models/test_project.py and src/backend/tests/test_models/test_asset.py files. Make sure you have tests for:

Creating instances of your models.

Updating fields.

Verifying relationships (Project-Asset).

Testing any constraints (e.g., the asset_type enum).

Testing timestamp updates (created_at, updated_at).

Testing cascade deletes.

These should also be consistent with the provided code.

6. Run Tests

From the root of your project, run:

docker-compose run api pytest -v src/backend/tests
content_copy
download
Use code with caution.
Bash

This will run all your backend tests (both API and model tests). Make sure they all pass before moving on. If any tests fail, carefully examine the error messages and debug your code.

This completes this part. Once all tests are passing and you've reviewed the code and structure, you can move on to the next part, which will focus on the PATCH endpoint and more advanced error handling. Let me know when you are ready to continue.
