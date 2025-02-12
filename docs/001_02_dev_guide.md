# Development Guide Review & Corrections

## Progress Tracking

### Database and Model Improvements
- [x] Fix Alembic configuration issues (env.py, settings)
- [x] Update alembic.ini with correct database URL
- [x] Regenerate initial migration
- [x] Add missing notes field to Project model
- [x] Fix Project and Asset model relationships
- [ ] Test migrations and model changes

### Celery Configuration
- [ ] Update celeryconfig.py to use settings from config.py
- [ ] Fix worker settings (prefetch, tasks per child)
- [ ] Set explicit task_always_eager
- [ ] Update project_tasks.py to use settings

### API Endpoint Logic
- [ ] Update create_project return type
- [ ] Fix list_projects query efficiency
- [ ] Add missing notes field to Project schema
- [ ] Add error handling to all endpoints

### Frontend Improvements
- [ ] Fix NEXT_PUBLIC_API_URL configuration
- [ ] Add missing type definitions
- [ ] Implement missing api.ts functions
- [ ] Add error handling to API calls
- [ ] Add loading states

### Testing
- [ ] Add basic endpoint tests
- [ ] Add Celery task tests
- [ ] Add frontend component tests

Okay, let's put on the Principal Software Engineer hat and do a thorough review of the project's foundation, identifying strengths, potential issues, and recommendations for corrections before you move into more intensive testing.

Review and Refinement of Recommendations

The core goal here is to ensure we have a rock-solid, testable, and understandable base before adding the complexities of video generation.

1. Database Migrations (Alembic):

Context: Alembic is essential for managing database schema changes over time. We need to get this right first. The issues identified were primarily about how env.py connects to the database and finds your models.

Review of alembic.ini:

sqlalchemy.url = postgresql+asyncpg://user:password@postgres:5432/content_platform
content_copy
download
Use code with caution.
Ini

Double-Check: The user, password, postgres (hostname), and content_platform (database name) must match the environment variables in your docker-compose.yml file for the postgres service. This is where many beginners trip up. If your docker-compose.yml uses different values, use those values here. This is the single most critical connection point.

Why postgres as the hostname? Because that's the name of your PostgreSQL service within the Docker network. Docker's internal DNS resolves postgres to the correct container's IP address.

Explicitly: This is not localhost from your host machine's perspective. It's localhost only from within another container in the same Docker network.

Review of env.py:

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# --- ADD THESE IMPORTS ---
import sys
sys.path.append('/app')  # Ensure your project is in the path
from src.backend.core.config import settings # Import your settings
from src.backend.models.project import Base  # Import your Base
# -------------------------

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata # Use your Base metadata


def run_migrations_offline() -> None:
    url = settings.DATABASE_URL # Use your settings!
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    # Use settings.DATABASE_URL directly
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        url=settings.DATABASE_URL,  # <---  Use settings here!
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
content_copy
download
Use code with caution.
Python

sys.path.append('/app'): This is crucial because your Dockerfile.api sets the WORKDIR to /app. Alembic runs within the container, so it needs to know where to find your project's code. This ensures that Python can find your src directory.

from src.backend.core.config import settings: We're directly using your settings object (which reads from your .env file) to get the DATABASE_URL. This is the correct way to ensure consistency.

from src.backend.models.project import Base: Alembic needs access to your model metadata to generate migrations. By importing Base, we give it that access. All your model classes (e.g., Project, Asset) must inherit from this Base.

target_metadata = Base.metadata: This line tells Alembic to use your model definitions as the source of truth for the database schema.

Simplified run_migrations_online: We've removed the unnecessary complexity and are directly using settings.DATABASE_URL.

Explicit Imports: Note the explicit import from src.backend.models.project import Base.

Regenerating the Migration:

Delete the old file: rm src/backend/migrations/versions/20250211_2248_05208814684b_initial_migration.py (or whatever the filename is).

Run autogeneration: docker-compose run api alembic revision --autogenerate -m "Create tables"

Inspect the new file: Open the newly generated migration file. It should contain op.create_table calls for your projects and assets tables, with all the correct columns and types. If it's still empty, there's a problem with how Alembic is finding your models (double-check the imports and target_metadata).

Apply the migration: docker-compose run api alembic upgrade head

2. Celery Configuration and Task Definition:

Context: Celery is your asynchronous task queue. It's critical for offloading long-running operations (like video processing) from your web server.

Review of src/backend/celeryconfig.py:

from src.backend.core.config import settings # Import settings

broker_url = settings.CELERY_BROKER_URL # Use settings
result_backend = settings.CELERY_RESULT_BACKEND # Use settings
broker_connection_retry_on_startup = True
broker_connection_retry = True

task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
enable_utc = True

worker_prefetch_multiplier = 1
worker_max_tasks_per_child = 10

task_always_eager = False # Set explicitly for production
content_copy
download
Use code with caution.
Python

from src.backend.core.config import settings: Crucial. We're using the same settings object as the rest of your application.

broker_url and result_backend: These are now correctly pulled from your settings. This ensures that Celery connects to the Redis instance defined in your docker-compose.yml.

task_always_eager = False: Explicitly set for production. During testing, you'll likely want to temporarily set this to True in your celery_config fixture (see Testing section below) to make tasks run synchronously.

Other settings: The other settings are good defaults for your project.

Review of src/backend/tasks/project_tasks.py:

from celery import Celery
from ..core.config import settings  # Import settings

celery = Celery(
    'project_tasks',
    broker=settings.CELERY_BROKER_URL,  # Use settings
    backend=settings.CELERY_RESULT_BACKEND,  # Use settings
)
# No need to call config_from_object, you've done it explicitly

@celery.task(name='test_task')
def test_task(x, y):
    return x + y
content_copy
download
Use code with caution.
Python

Direct Celery Instantiation: This is a more explicit and often clearer way to configure Celery than using config_from_object.

Using settings: Again, we're ensuring consistency by using your centralized settings.

@celery.task(name='test_task'): Explicitly naming your tasks is a good practice, especially as you add more.

3. API Endpoint Logic (src/backend/api/routers/projects.py):

Context: These are the entry points for your frontend to interact with the backend. They need to be robust, well-typed, and consistent.

Corrections Review: The provided corrections are good. The key changes are:

@router.post("/", response_model=ProjectSchema)  # Return the full schema
    async def create_project(
        project_create: ProjectCreate,
        db: AsyncSession = Depends(get_db)
    ):
        db_project = Project(
            topic=project_create.topic,
            notes=project_create.notes,  # Include notes
            status="CREATED"
        )
        db.add(db_project)
        await db.commit()
        await db.refresh(db_project)
        return db_project  # Return the full object
content_copy
download
Use code with caution.
Python
@router.get("/", response_model=List[ProjectSchema])
     async def list_projects(
         db: AsyncSession = Depends(get_db)
     ):
         result = await db.execute(select(Project))  # Use select
         projects = result.scalars().all()  # Get Project instances
         return projects
content_copy
download
Use code with caution.
Python

response_model=ProjectSchema: Returning the full Pydantic schema is best practice.

Using select(Project) and scalars().all(): This is the most efficient and correct way to fetch your Project objects.

Consistency: The corrected code is consistent in its use of Pydantic models and SQLAlchemy.

notes field: The notes field has been added to the Project object.

4. Project and Asset Models:

Context: These define the structure of your data in the database.

Corrections Review:

Explicit Imports: Using from src.backend.models.project import Base is better for testability and clarity.

notes field: The notes field is correctly added to the Project model.

Relationships: The relationship definitions look correct.

5. Frontend (Initial Setup):

Context: The frontend is your user interface. The initial focus is on getting the basic communication with the backend working.

Review of src/frontend/lib/api.ts:

// src/frontend/lib/api.ts
import axios from 'axios';
import { ProjectCreate, Project as ProjectSchema, ProjectStatus } from '@/types'; // Import the types


const getApiUrl = () => {
  if (typeof window === 'undefined') {
    // Server-side (Next.js API routes, etc.) - use the environment variable
    return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  } else {
    // Client-side - assume same origin (works if frontend is served from Next.js dev server)
    return ''; //  Empty string uses the current origin
  }
};

const api = axios.create({
  baseURL: getApiUrl(),
});

export const projectsApi = {
  create: async (data: ProjectCreate): Promise<ProjectSchema> => {
    const response = await api.post('/projects', data);
    return response.data;
  },

  getStatus: async (projectId: string): Promise<ProjectStatus> => {
    const response = await api.get(`/projects/${projectId}/status`);
    return response.data;
  },
};

export type { ProjectCreate, ProjectSchema, ProjectStatus };
content_copy
download
Use code with caution.
TypeScript

getApiUrl() Function: This is a very important improvement. It handles the difference between server-side rendering (SSR) in Next.js and client-side rendering.

typeof window === 'undefined': This check determines if the code is running on the server (where window is not defined) or in the browser.

Server-Side: It uses process.env.NEXT_PUBLIC_API_URL. This is the correct way to access environment variables in Next.js. You'll still set this to your M2 Max's IP address during development.

Client-Side: It returns an empty string (''). This tells axios to use the current origin (the same host and port where the frontend is being served from). This is crucial because during development, your Next.js frontend runs on http://localhost:3000 (typically), while your API is on http://<M2_Max_IP>:8000. By using an empty string, the browser will automatically make requests to http://localhost:3000/projects, which Next.js will then proxy to your backend (thanks to the rewrites configuration in next.config.js - which we need to add).

axios.create(): Creating an axios instance with a base URL is good practice.

Type Definitions: Importing and using your TypeScript types (ProjectCreate, ProjectSchema, ProjectStatus) is excellent.

Add rewrites to next.config.js:

We need to tell Next.js to proxy api requests to our backend.

// src/frontend/next.config.js
  /** @type {import('next').NextConfig} */
  const nextConfig = {
    reactStrictMode: true,
    swcMinify: true,
    async rewrites() { // Add this rewrites configuration
      return [
        {
          source: '/projects/:path*',
          destination: `${process.env.NEXT_PUBLIC_API_URL}/projects/:path*`,
        },
        {
          source: '/health',
          destination: `${process.env.NEXT_PUBLIC_API_URL}/health`,
        },
      ];
    },
  }

  module.exports = nextConfig;
content_copy
download
Use code with caution.
JavaScript

Review of src/frontend/types/index.d.ts:

// src/frontend/types/index.d.ts
    export interface Project {
      id: string;
      name: string | null;
      topic: string;
      status: string;
      created_at: string;
      updated_at: string;
    }

    export interface ProjectCreate {
      topic: string;
      notes?: string;
    }

    export interface ProjectStatus {
        status: string;
    }
content_copy
download
Use code with caution.
TypeScript

The type definitions correctly mirror the backend schema.

Review of src/frontend/app/projects/[projectId]/page.tsx:

This is now correctly using string for projectId.

The useEffect hook and polling are a good starting point for getting project status.

6. General Code Quality and Best Practices (Reinforcement):

Type Hints: Continue to use type hints everywhere. This is one of your project's strengths.

Error Handling: This is where you need to focus next.

Backend:

Wrap your database operations in try...except blocks. Catch sqlalchemy.exc.IntegrityError (for unique constraint violations), sqlalchemy.exc.OperationalError (for connection problems), and generic Exception for unexpected errors.

Use HTTPException to return appropriate HTTP status codes and informative error messages in a consistent JSON format (e.g., {"error": "Database error", "detail": "..."}).

Frontend:

Use try...catch around your axios calls.

Display user-friendly error messages (e.g., using toast notifications).

Consider using a state management library (like React Query or Zustand) to handle loading and error states more elegantly. React Query is a particularly good fit for data fetching.

Logging: Add logger.info(), logger.debug(), and logger.error() calls to your API endpoints and Celery tasks. For example:

@router.post("/", response_model=ProjectSchema)
async def create_project(
    project_create: ProjectCreate,
    db: AsyncSession = Depends(get_db)
):
    logger.info(f"Creating project with topic: {project_create.topic}") # Log the topic
    try:
        db_project = Project(
            topic=project_create.topic,
            notes=project_create.notes,
            status="CREATED"
        )
        db.add(db_project)
        await db.commit()
        await db.refresh(db_project)
        return db_project
    except Exception as e:
        logger.error(f"Error creating project: {e}") # Log the error
        raise HTTPException(status_code=500, detail="Internal server error")
content_copy
download
Use code with caution.
Python

7. Testing (Crucial Next Step):

conftest.py: You'll need to set up fixtures here for your tests. Here's a basic example that you'll need to adapt:

# src/backend/tests/conftest.py
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.backend.main import app  # Import your FastAPI app
from src.backend.core.config import settings
from src.backend.core.database import Base, get_db
from src.backend.models.project import Project  # Import your models
from src.backend.models.asset import Asset


# Use a separate test database
TEST_DATABASE_URL = "postgresql+asyncpg://user:password@localhost/test_dbname"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestSessionLocal = sessionmaker(
    bind=test_engine, expire_on_commit=False, class_=AsyncSession
)

# Fixture to create and drop tables before/after each test
@pytest.fixture(scope="function")
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# Fixture for database session
@pytest.fixture(scope="function")
async def db_session():
    async with TestSessionLocal() as session:
        yield session

# Fixture for httpx AsyncClient (for making requests to your API)
@pytest.fixture(scope="module")
async def client():
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c

@pytest.fixture(scope="function", autouse=True)
def override_settings(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    #Import settings and override database url
    settings.DATABASE_URL = TEST_DATABASE_URL
content_copy
download
Use code with caution.
Python

Test Files: Create files like src/backend/tests/test_api/test_projects.py to test your API endpoints. Use the fixtures you define in conftest.py. Example:

# src/backend/tests/test_api/test_projects.py
import pytest
from httpx import AsyncClient
from src.backend.schemas.project import ProjectCreate

@pytest.mark.asyncio
async def test_create_project(client: AsyncClient, setup_database):  # Use fixtures
    data = ProjectCreate(topic="Test Topic", notes="Test Notes").model_dump()
    response = await client.post("/projects/", json=data)
    assert response.status_code == 200
    project = response.json()
    assert project["topic"] == "Test Topic"
    assert project["notes"] == "Test Notes"
    assert project["status"] == "CREATED"
    assert "id" in project  # Check for UUID


@pytest.mark.asyncio
async def test_get_project_status(client: AsyncClient, setup_database):
    # First, create a project
    create_data = ProjectCreate(topic="Test Topic", notes="Test Notes").model_dump()
    create_response = await client.post("/projects/", json=create_data)
    assert create_response.status_code == 200
    project_id = create_response.json()["id"]

    # Now, get its status
    status_response = await client.get(f"/projects/{project_id}/status")
    assert status_response.status_code == 200
    status = status_response.json()
    assert status["status"] == "CREATED"

@pytest.mark.asyncio
async def test_get_project_status_not_found(client: AsyncClient, setup_database):
    response = await client.get(f"/projects/aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee/status")  # Invalid UUID
    assert response.status_code == 404
    assert response.json() == {"detail": "Project not found"}

@pytest.mark.asyncio
async def test_list_projects(client: AsyncClient, setup_database):
    # Add a project.
    project_data = ProjectCreate(topic='test_topic', notes='test_notes')
    response = await client.post("/projects/", json=project_data.model_dump())
    assert response.status_code == 200

    # list projects
    response = await client.get('/projects/')
    result = response.json()
    assert response.status_code == 200
    assert type(result) == list
    assert len(result) >= 1
content_copy
download
Use code with caution.
Python

Celery Testing:

# src/backend/tests/test_tasks/test_project_tasks.py
import pytest
from src.backend.tasks.project_tasks import celery, test_task

@pytest.fixture(scope="session")
def celery_config():
    return {
        'broker_url': 'memory://',  # Use in-memory broker for testing
        'result_backend': 'rpc://', # Use RPC backend
        'task_always_eager': True,  # Run tasks synchronously
        'task_eager_propagates': True,
    }

@pytest.mark.celery
def test_test_task(celery_app):
    result = test_task.delay(2, 3)
    assert result.get() == 5
    assert result.successful()
content_copy
download
Use code with caution.
Python

task_always_eager = True: This is critical for testing Celery tasks. It makes them run synchronously, so you can directly assert their results.

broker_url = 'memory://' and result_backend = 'rpc://': These settings configure Celery to use in-memory transport for testing, which is faster and doesn't require a running Redis instance.

Final Summary and Actionable Steps:

Migrations:

Fix alembic.ini: Ensure the sqlalchemy.url is correct, using your docker-compose.yml values.

Fix env.py: Use the corrected code provided above. Ensure sys.path.append('/app') is present. Use settings.DATABASE_URL.

Delete and Regenerate: Remove the old, empty migration file. Run alembic revision --autogenerate again. Inspect the new file.

Apply Migration: Use alembic upgrade head

Celery:

celeryconfig.py: Use the settings object to get broker_url and result_backend.

project_tasks.py: Use the settings object when creating the Celery instance.

task_always_eager = False: Ensure it is explicitly set in the config.

API Endpoints:

Use response_model=ProjectSchema for create_project.

Use select(Project) and scalars().all() in list_projects.

Add the notes field.

Models:

Use explicit imports (from src.backend.models.project import Base).

Verify notes field exists in Project model.

Frontend:

lib/api.ts: Implement the getApiUrl() function as shown above.

types/index.d.ts: Define the Project interface.

next.config.js: Add proxy configuration

Error Handling:

Add try/except blocks around all database operations and API calls.

Logging:

Add logger.info(), logger.debug(), and logger.error() calls.

Testing:

conftest.py: Create the fixtures as shown above (database setup, session, client, settings override). Crucially, use a separate test database.

Write Tests: Create test files (e.g., test_projects.py) and write tests for each API endpoint and your Celery task, using the fixtures.

By following these steps meticulously, you'll have a robust, well-tested, and well-structured foundation for your project. This will make future development much smoother and less error-prone. Good luck!