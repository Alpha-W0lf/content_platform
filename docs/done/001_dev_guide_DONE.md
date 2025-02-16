# Content Platform Development Guide

## Progress Tracking

### Phase 1: Project Structure and Initial Setup
- [✓] Step 1: Create Core Directory Structure
- [✓] Step 2: Initialize Git
- [✓] Step 3: Populate Initial Files (Backend - FastAPI)
- [✓] Step 4: Populate Initial Files (Frontend - Next.js)
- [✓] Step 5: Install Dependencies (Backend)
- [✓] Step 6: Install Dependencies (Frontend)
- [✓] Step 7: Install shadcn/ui components (Note: Calendar component failed to install)
- [✓] Step 8: Initial Alembic Setup (Backend)
- [✓] Step 9: Run and Test

Okay, here's your precise, step-by-step guide for setting up the project structure, combining the directory creation with the initial task guidance. This incorporates everything we've discussed, making it your actionable development plan.

Phase 1: Project Structure and Initial Setup

Step 1: Create the Core Directory Structure

Execute these commands in your terminal (from the directory where you want to create your project):

mkdir -p alpha-w0lf-content_platform/src/backend/api/routers
mkdir -p alpha-w0lf-content_platform/src/backend/core
mkdir -p alpha-w0lf-content_platform/src/backend/models
mkdir -p alpha-w0lf-content_platform/src/backend/schemas
mkdir -p alpha-w0lf-content_platform/src/backend/modules
mkdir -p alpha-w0lf-content_platform/src/backend/prompts
mkdir -p alpha-w0lf-content_platform/src/backend/tasks
mkdir -p alpha-w0lf-content_platform/src/backend/migrations/versions
mkdir -p alpha-w0lf-content_platform/src/backend/tests/test_api
mkdir -p alpha-w0lf-content_platform/src/backend/tests/test_models
mkdir -p alpha-w0lf-content_platform/src/backend/tests/test_modules
mkdir -p alpha-w0lf-content_platform/src/frontend/app
mkdir -p alpha-w0lf-content_platform/src/frontend/components
mkdir -p alpha-w0lf-content_platform/src/frontend/lib
mkdir -p alpha-w0lf-content_platform/src/frontend/styles
mkdir -p alpha-w0lf-content_platform/src/frontend/types
mkdir -p alpha-w0lf-content_platform/src/frontend/public
mkdir -p alpha-w0lf-content_platform/.docker
mkdir -p alpha-w0lf-content_platform/data/projects
mkdir -p alpha-w0lf-content_platform/docs
mkdir -p alpha-w0lf-content_platform/.github
cd alpha-w0lf-content_platform

# Create __init__.py files
touch src/backend/__init__.py
touch src/backend/api/__init__.py
touch src/backend/api/routers/__init__.py
touch src/backend/core/__init__.py
touch src/backend/models/__init__.py
touch src/backend/schemas/__init__.py
touch src/backend/modules/__init__.py
touch src/backend/prompts/__init__.py
touch src/backend/tasks/__init__.py
touch src/backend/migrations/__init__.py
touch src/backend/tests/__init__.py
touch src/backend/tests/test_api/__init__.py
touch src/backend/tests/test_models/__init__.py
touch src/backend/tests/test_modules/__init__.py
touch src/frontend/app/__init__.py
touch src/frontend/components/__init__.py
touch src/frontend/lib/__init__.py
touch src/frontend/types/__init__.py


# Create initial files
touch src/backend/main.py
touch src/backend/api/routers/projects.py
touch src/backend/api/dependencies.py
touch src/backend/core/config.py
touch src/backend/core/database.py
touch src/backend/core/utils.py
touch src/backend/models/project.py
touch src/backend/models/asset.py
touch src/backend/schemas/project.py
touch src/backend/schemas/asset.py
touch src/backend/tasks/project_tasks.py
touch src/backend/celeryconfig.py
touch src/backend/migrations/env.py
touch src/backend/migrations/script.py.mako
touch src/backend/tests/conftest.py
touch src/frontend/app/page.tsx
touch src/frontend/app/layout.tsx
touch src/frontend/lib/api.ts
touch src/frontend/styles/globals.css
touch src/frontend/types/index.d.ts
touch src/frontend/.env.local
touch src/frontend/.eslintrc.json
touch src/frontend/.prettierrc.json
touch src/frontend/next.config.js
touch src/frontend/package.json
touch src/frontend/postcss.config.js
touch src/frontend/tailwind.config.js
touch src/frontend/tsconfig.json
touch .docker/Dockerfile.api
touch .docker/Dockerfile.celery
touch .gitignore
touch docker-compose.yml
touch LICENSE
touch README.md
mkdir -p alpha-w0lf-content_platform/src/frontend/app/projects/[projectId]
mkdir -p alpha-w0lf-content_platform/src/frontend/app/(auth)/sign-in/[[...sign-in]]
mkdir -p alpha-w0lf-content_platform/src/frontend/app/(auth)/sign-up/[[...sign-up]]
touch alpha-w0lf-content_platform/src/frontend/app/projects/[projectId]/page.tsx
touch alpha-w0lf-content_platform/src/frontend/app/projects/page.tsx
touch alpha-w0lf-content_platform/src/frontend/app/(auth)/sign-in/[[...sign-in]]/page.tsx
touch alpha-w0lf-content_platform/src/frontend/app/(auth)/sign-up/[[...sign-up]]/page.tsx
touch src/frontend/lib/auth.ts
content_copy
download
Use code with caution.
Bash

Step 2: Initialize Git

git init
git add .
git commit -m "Initial project structure"
content_copy
download
Use code with caution.
Bash

Step 3: Populate Initial Files (Backend - FastAPI)

.docker/Dockerfile.api: (Basic Python + FastAPI setup - adjust as needed for dependencies)

FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/backend /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
content_copy
download
Use code with caution.
Dockerfile

src/backend/main.py: (Basic FastAPI setup)

from fastapi import FastAPI
from .api.routers import projects
from .core.config import settings
from .core.database import engine
from .models import Base  # Import your base model

app = FastAPI(title=settings.PROJECT_NAME, version=settings.API_VERSION)

# Include routers
app.include_router(projects.router)

@app.on_event("startup")
async def startup_event():
    # Create tables (using the Base.metadata)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/health")
async def health():
    return {"status": "OK"}
content_copy
download
Use code with caution.
Python

src/backend/api/routers/projects.py: (Initial /projects endpoints)

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ...core.database import get_db
from ...models.project import Project
from ...schemas.project import ProjectCreate, ProjectStatus
from uuid import UUID, uuid4

router = APIRouter(
    prefix="/projects",
    tags=["projects"],
)

@router.post("/", response_model=dict)  # Return a simple dict for now
async def create_project(project_create: ProjectCreate, db: AsyncSession = Depends(get_db)):
    project = Project(id=uuid4(), name=project_create.topic, topic=project_create.topic, status="CREATED")
    db.add(project)
    await db.commit()
    await db.refresh(project)  # Refresh to get the created_at timestamp
    return {"project_id": str(project.id)}


@router.get("/{project_id}/status", response_model=ProjectStatus)
async def get_project_status(project_id: UUID, db: AsyncSession = Depends(get_db)):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectStatus(status=project.status)
content_copy
download
Use code with caution.
Python

src/backend/api/dependencies.py: (Database dependency)

from sqlalchemy.ext.asyncio import AsyncSession
from ..core.database import SessionLocal

async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session
content_copy
download
Use code with caution.
Python

src/backend/core/config.py: (Configuration using Pydantic Settings)

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Alpha Wolf Content Platform"
    API_VERSION: str = "v0.0"
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/dbname" #change these credentials
    # Add other settings (Celery, etc.) as needed

    class Config:
        env_file = ".env"  # Load from .env file in the backend directory

settings = Settings()
content_copy
download
Use code with caution.
Python

Create a .env file in the src/backend directory to store environment variables:

DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname #replace with actual credentials
content_copy
download
Use code with caution.

src/backend/core/database.py: (SQLAlchemy setup)

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from .config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True)  # Set echo=True for debugging
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
content_copy
download
Use code with caution.
Python

src/backend/core/utils.py: (Empty for now - add utility functions later)

# Utility functions will go here
content_copy
download
Use code with caution.
Python

src/backend/models/project.py: (Project model)

from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base() #create declarative base

class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    status = Column(String)
    topic = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    assets = relationship("Asset", back_populates="project")
content_copy
download
Use code with caution.
Python

src/backend/models/asset.py: (Asset model)

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from .project import Base  # Import Base from project.py

class Asset(Base):
    __tablename__ = "assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    asset_type = Column(String)
    path = Column(String)
    approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="assets")
content_copy
download
Use code with caution.
Python

src/backend/schemas/project.py: (Pydantic schemas)

from pydantic import BaseModel, UUID4
from typing import Optional

class ProjectCreate(BaseModel):
    topic: str
    notes: Optional[str] = None  # Optional notes

class ProjectStatus(BaseModel):
    status: str
content_copy
download
Use code with caution.
Python

src/backend/schemas/asset.py:

from pydantic import BaseModel, UUID4
 from typing import Optional

 class AssetCreate(BaseModel):
     project_id: UUID4
     asset_type: str
     path: str
     approved: Optional[bool] = False
content_copy
download
Use code with caution.
Python

src/backend/tasks/project_tasks.py: (Empty for now, just define the Celery app)

from celery import Celery
from ..core.config import settings

celery = Celery(__name__)
celery.config_from_object('src.backend.celeryconfig')

@celery.task
def test_task():
  print("this is a test")
content_copy
download
Use code with caution.
Python

src/backend/celeryconfig.py:

broker_url = 'redis://localhost:6379/0'  # Update with your Redis URL
result_backend = 'redis://localhost:6379/0'  # Update with your Redis URL
content_copy
download
Use code with caution.
Python

Add redis://localhost:6379/0 to the backend .env file.

src/backend/migrations/env.py: (Modify the env.py file generated by Alembic to use asyncpg and your models)

# env.py - modified for asyncpg
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
from src.backend.models.project import Base  # Import your Base
target_metadata = Base.metadata


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    from src.backend.core.config import settings #import settings
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.DATABASE_URL #get url

    connectable = await sync_engine_to_async_engine(
        engine_from_config(
            configuration,
            prefix="sqlalchemy.",
            poolclass=pool.AsyncAdaptedQueuePool,
        )
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

# --- End of changes for asyncpg
import asyncio
from sqlalchemy.ext.asyncio import AsyncEngine

def sync_engine_to_async_engine(sync_engine):
    """
    Convert a synchronous SQLAlchemy engine to an asynchronous one.
    """
    return AsyncEngine(sync_engine)

if context.is_offline_mode():
    run_migrations_offline()
else:
  asyncio.run(run_migrations_online())
content_copy
download
Use code with caution.
Python

src/backend/migrations/script.py.mako: This file does not typically need modification.

src/backend/tests/conftest.py:

import pytest
#add pytest fixtures here as you need them
content_copy
download
Use code with caution.
Python

Step 4: Populate Initial Files (Frontend - Next.js)

src/frontend/app/page.tsx: (Basic home page)

export default function Home() {
  return (
    <div>
      <h1>Welcome to the Alpha Wolf Content Platform</h1>
      {/* Add your initial UI elements here */}
    </div>
  );
}
content_copy
download
Use code with caution.
TypeScript

src/frontend/app/layout.tsx: (Basic layout)

import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Create Next App",
  description: "Generated by create next app",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
content_copy
download
Use code with caution.
TypeScript

src/frontend/lib/api.ts: (Empty for now - add API functions later)

// API interaction functions will go here
content_copy
download
Use code with caution.
TypeScript

src/frontend/app/(auth)/sign-in/[[...sign-in]]/page.tsx:

import { SignIn } from "@clerk/nextjs";

export default function Page() {
  return (
    <div className="flex justify-center items-center h-screen">
      <SignIn />
    </div>
  );
}
content_copy
download
Use code with caution.
TypeScript

src/frontend/app/(auth)/sign-up/[[...sign-up]]/page.tsx:

import { SignUp } from "@clerk/nextjs";

export default function Page() {
  return (
    <div className="flex justify-center items-center h-screen">
      <SignUp />
    </div>
  );
}
content_copy
download
Use code with caution.
TypeScript

src/frontend/lib/auth.ts:

//add authentication functions here
content_copy
download
Use code with caution.
TypeScript

src/frontend/app/projects/[projectId]/page.tsx:

export default function Page() {
    return (
      <div>
        <h1>Project Detail</h1>
      </div>
    );
}
content_copy
download
Use code with caution.
TypeScript

src/frontend/app/projects/page.tsx:

export default function Page() {
    return (
      <div>
        <h1>Project List Page</h1>
      </div>
    );
  }
content_copy
download
Use code with caution.
TypeScript

src/frontend/styles/globals.css: Add global styles as needed. Tailwind will handle most styling.

src/frontend/types/index.d.ts: Add global TypeScript types as needed.

.env.local, .eslintrc.json, .prettierrc.json, next.config.js, package.json, postcss.config.js, tailwind.config.js, tsconfig.json: These are standard configuration files. You can generate most of them using the npx create-next-app command (which you likely already did). Make sure to install necessary packages (npm install ...). Pay close attention to instructions for configuring tailwind css and shadcn/ui.

.env.local:

NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key
CLERK_SECRET_KEY=your_clerk_secret_key
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/
content_copy
download
Use code with caution.

.gitignore:

# Node
node_modules
.next/
out/

# Python
venv/
__pycache__/
*.pyc
.env

# Data
data/

# OS-specific
.DS_Store

# VS Code
.vscode/
content_copy
download
Use code with caution.

docker-compose.yml:

version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: .docker/Dockerfile.api
    ports:
      - "8000:8000"
    volumes:
      - ./src/backend:/app
    depends_on:
      - postgres
      - redis
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/dbname # Use service name for host
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0

  celery_worker:
    build:
      context: .
      dockerfile: .docker/Dockerfile.celery
    volumes:
      - ./src/backend:/app
    depends_on:
      - api
      - redis
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/dbname # Use service name for host
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0

  postgres:
    image: postgres:latest
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: dbname
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:latest
    ports:
      - "6379:6379"

volumes:
  postgres_data:
content_copy
download
Use code with caution.
Yaml

Dockerfile.celery:

FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/backend /app
# COPY . . #this causes an error

CMD ["celery", "-A", "src.backend.tasks.project_tasks:celery", "worker", "-l", "info"]
content_copy
download
Use code with caution.

LICENSE: (Choose a license, e.g., MIT, and put the license text here)

README.md: (Provide a brief project overview and setup instructions)

Step 5: Install Dependencies (Backend)
Create a requirements.txt file in the root of your backend directory (alpha-w0lf-content_platform/):

fastapi
uvicorn[standard]
sqlalchemy
asyncpg
alembic
pydantic
pydantic-settings
celery
redis
python-dotenv
content_copy
download
Use code with caution.

Install these dependencies using pip inside the Docker container (once you've built it). A good way to do this initially is to run:

docker-compose build api
docker-compose run api pip install -r requirements.txt
content_copy
download
Use code with caution.
Bash

You will need to install in the celery container as well.

Step 6: Install Dependencies (Frontend)

Navigate to your frontend directory (src/frontend) and install dependencies using npm or yarn:

cd src/frontend
npm install
#or
yarn install
content_copy
download
Use code with caution.
Bash

Install other necessary dependencies, such as:

npm install @clerk/nextjs
npm install axios
#or
yarn add @clerk/nextjs
yarn add axios
content_copy
download
Use code with caution.

Step 7: Initial Alembic Setup (Backend)

Initialize Alembic: From within your backend Docker container (or in a local virtual environment if you're testing outside Docker), run:

docker-compose run api alembic init migrations
content_copy
download
Use code with caution.
Bash

This creates the migrations directory and configuration files.

Configure Alembic: Edit migrations/env.py as described above to connect to your database and use your models.

Create Initial Migration:

docker-compose run api alembic revision --autogenerate -m "Create projects and assets tables"
content_copy
download
Use code with caution.
Bash

This will generate a migration file in migrations/versions/.

Apply Migration:

docker-compose run api alembic upgrade head
content_copy
download
Use code with caution.
Bash

This applies the migration and creates the tables in your database.

Step 8: Run and Test

Start Services:

docker-compose up --build
content_copy
download
Use code with caution.
Bash

Use docker-compose up -d --build to run in detached mode.

Test FastAPI: Open your browser and go to http://localhost:8000/health. You should see {"status": "OK"}.

Test Next.js: Your Next.js app should be running on http://localhost:3000.

Test Clerk: visit the sign in and sign up pages.

Phase 2: Continue with the Task List

Now that you have the basic structure and initial setup complete, you can continue with the rest of the prioritized task list (v0.0 and v0.1), creating files and directories as needed within this established structure. Remember to test frequently and commit your code regularly. Remember to install dependencies in the appropriate containers as you add new packages. This comprehensive guide sets you up for a well-organized and efficient development process.
