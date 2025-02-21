# Content Platform Development Guide - Part 4: Task Error Handling and Frontend Integration

This is Part 4 of 4 in the Content Platform Development Guide series:

- Part 1: Project Setup and Initial API/Model Tests
- Part 2: PATCH Endpoint and Error Handling
- Part 3: Task Testing and Request Logging
- Part 4 (Current): Task Error Handling and Frontend Integration

Okay, let's move on to the next part. This part will focus on:

1.  **Integrating Error Handling and Status Updates into the `process_project` Celery Task:** We'll add basic error handling and status updates to the `process_project` task, even though the task itself is still a placeholder. This will give us a framework to test against.
2.  **Adding Task Logging:** We'll add logging to the Celery task.
3.  **Testing Task Failure:** We'll add a test case to simulate and verify task failure handling.
4.  **Connecting the Frontend**: We will start making api calls from the Next.js frontend.

````markdown
# Content Platform Development and Testing Guide

This part builds on the previous part, adding error handling and status updates to the Celery task, adding task logging, testing task failure handling, and connecting the Next.js frontend to the FastAPI backend.

**Remember to always:**

- **Follow Best Practices:** Clear naming, docstrings, small functions, PEP 8.
- **Maintainable Code:** Easy to understand, modify, and extend. Use comments to explain _why_.
- **Targeted Changes:** Small, incremental changes. Commit frequently.
- **Modularity and Extensibility:** Design for future features. Use dependency injection and clear interfaces.
- **Test Driven Development:** Write tests before code.

## Task Tracking (v0.0 Foundation)

### Implemented ✓

(All items from previous parts)

- [x] Project structure and directory setup
- [x] Database Setup
- [x] API Setup
- [x] Authentication
- [x] Frontend Foundation
- [x] Task Queue
- [x] Linting and Formatting
- [x] Testing Infrastructure
- [x] API Tests (`src/backend/tests/test_api/test_projects.py`)
- [x] Model Tests
- [x] Task Tests
  - [x] Celery configuration tests
  - [x] Task execution tests (`test_task`)
- [x] Error Handling
  - [x] Database Operations
  - [x] API Endpoints
- [x] Logging System
  - [x] JSON logging setup
  - [x] Log levels configuration
  - [x] Request logging (middleware)
  - [x] Error logging

### In Progress 🚧

- [x] **Task Tests**
  - [x] Celery configuration tests
  - [x] Task execution tests (`test_task`)
  - [x] Task error handling _<-- Add test for process_project failure_
- [ ] **Error Handling (Enhancements)** _<-- Add conflict handling_
  - [ ] API Endpoints
    - [ ] Conflict handling
  - [x] **Task Processing** _<-- Integrate error handling & status updates_
    - [x] Task failure handling
    - [ ] Retry logic
    - [x] Status updates
- [x] **Logging System**

  - [x] Task logging _<-- Add logging to process_project_

- [ ] Start Connecting Frontend _<--- Add project list to the Next.js frontend_

### Next Steps 📋

1.  **Complete Celery Task Implementation:** Add the core logic to `process_project`.
2.  **Implement Retry Logic:** Add retry logic to `process_project`.
3.  **Conflict Handling (API):** Consider adding conflict handling to your API (e.g., for duplicate project topics).
4.  **Advanced Testing:** (Later) Consider mocking/integration tests for database connection errors.
5.  **Continue Frontend Integration**: Add more UI elements that use the backend API.

## 1. Celery Task Enhancements (`process_project`)

We'll modify `src/backend/tasks/project_tasks.py` to include:

- Status updates to the `Project` model.
- Error handling with `try...except`.
- Logging.

```python
# src/backend/tasks/project_tasks.py
import logging
from celery import shared_task
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core.database import AsyncSessionLocal  # Import AsyncSessionLocal
from src.backend.models.project import Project
from src.backend.schemas.project import ProjectStatus
from sqlalchemy import select

logger = logging.getLogger(__name__)

@shared_task(bind=True)
async def process_project(self, project_id: str) -> None:
    """
    Process a project asynchronously.
    Args:
        self: The Celery task instance (automatically provided by bind=True).
        project_id: The UUID of the project to process.
    """
    logger.info(f"Task process_project started for project_id: {project_id}")

    # Database operations *must* be within an async context
    async with AsyncSessionLocal() as db:
        try:
            # Get the project
            result = await db.execute(select(Project).where(Project.id == project_id))
            project = result.scalar_one_or_none()
            if project is None:
                logger.error(f"Project not found: {project_id}")
                # No need to raise here; the task can just return
                return

            # Update status to PROCESSING
            project.status = ProjectStatus.PROCESSING
            await db.commit()
            await db.refresh(project) #Refresh to use updated values
            logger.info(f"Project status updated to PROCESSING: {project_id}")

            # --- Simulate work (REPLACE WITH ACTUAL PROCESSING) ---
            # In a real application, this is where you'd call your
            # modules for script generation, asset creation, etc.
            import time  # Use asyncio.sleep for real async operations
            time.sleep(5)  # Simulate 5 seconds of work
            # --- End of simulated work ---

            # Update status to COMPLETED
            project.status = ProjectStatus.COMPLETED
            await db.commit()
            logger.info(f"Project status updated to COMPLETED: {project_id}")

        except Exception as e:
            await db.rollback()  # Rollback on any error
            logger.error(f"Task process_project failed for project_id: {project_id}", exc_info=True)
            # Update project status to ERROR in the database
            if project: #Check the project is not none
                project.status = ProjectStatus.ERROR
                await db.commit()
            raise  # Re-raise the exception so Celery knows the task failed

```
````

Key Changes:

- **Import `AsyncSessionLocal`:** We now import `AsyncSessionLocal` directly, as we need to create a database session _within_ the task. Celery tasks run in a separate process, so they don't have access to the FastAPI dependency injection.
- **`async with AsyncSessionLocal() as db:`:** This creates a new database session for each task execution. It's _crucial_ to use `async with` to ensure the session is properly closed, even if errors occur.
- **Database Operations:** All database interactions (getting the project, updating the status) are now done within the `async with` block.
- **Status Updates:** We update the `project.status` to `PROCESSING` at the beginning and `COMPLETED` at the end (or `ERROR` if an exception occurs). We use `await db.commit()` to save the changes and `await db.refresh()` to update the project with values.
- **Error Handling:** The `try...except` block catches _any_ exception, logs it (including the stack trace), rolls back the transaction, updates the project status to `ERROR`, and then _re-raises_ the exception. Re-raising is important: it tells Celery that the task failed, which is necessary for Celery's retry and error handling mechanisms to work.
- **Logging:** We use `logger.info` and `logger.error` to log the progress and any errors. The `f"..."` strings make it easy to include variables in the log messages.
- **Project None Check**: Check if the project variable is None before attempting to modify the database.
- **Simulated Work:** The `time.sleep(5)` is just a placeholder. Replace this with your actual project processing logic. Remember to use `asyncio.sleep()` if you need to wait within an asynchronous task.

## 2. Celery Task Tests (Updated)

Now, update `src/backend/tests/test_tasks/test_project_tasks.py` to test the `process_project` task more thoroughly, including a failure case:

```python
# src/backend/tests/test_tasks/test_project_tasks.py
import pytest
from src.backend.tasks.project_tasks import celery, test_task, process_project
from celery.exceptions import Ignore
from src.backend.models.project import Project
from src.backend.schemas.project import ProjectStatus
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

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

@pytest.mark.asyncio
@pytest.mark.celery  # Add the celery marker
async def test_process_project_task(db_session: AsyncSession):  # Inject db_session
    """Tests successful process_project execution."""

    # 1. CREATE A PROJECT
    project = Project(id=uuid.uuid4(), topic="Test Topic", notes="Test Notes", status=ProjectStatus.CREATED)
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)  # Refresh to get the latest state

    # 2. RUN THE TASK
    result = process_project.delay(str(project.id))  # Pass project ID as a string
    assert result.successful()

    # 3. VERIFY DATABASE CHANGES
    await db_session.refresh(project)  # Refresh to get changes made by the task
    assert project.status == ProjectStatus.COMPLETED

@pytest.mark.asyncio
@pytest.mark.celery
async def test_process_project_task_failure(db_session: AsyncSession):
    """Tests process_project failure scenario."""

    # 1. CREATE A PROJECT (to test status update on failure)
    project = Project(id=uuid.uuid4(), topic="Test Topic", status=ProjectStatus.CREATED)
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)


    # 2. RUN THE TASK WITH AN INVALID ID (to simulate an error)
    invalid_project_id = "invalid-id"  # Not a UUID
    result = process_project.delay(invalid_project_id)

    # 3. ASSERT TASK FAILURE
    assert result.failed()  # Celery should mark the task as failed

    # 4. VERIFY DATABASE CHANGES (status should be ERROR)
    retrieved_project = await db_session.get(Project, project.id)  # Use get, not execute/scalar_one
    assert retrieved_project.status == ProjectStatus.ERROR  # Status updated

@pytest.mark.asyncio
@pytest.mark.celery
async def test_process_project_task_project_not_found(db_session: AsyncSession):
    """Tests process_project when the project ID is valid but doesn't exist."""
    non_existent_uuid = str(uuid.uuid4())
    result = process_project.delay(non_existent_uuid)
    assert result.successful() #It should still complete even with project not found

```

Key Changes and Explanations:

- **`db_session` Fixture:** We now inject the `db_session` fixture into the test functions. This is _essential_ for interacting with the database within the test.
- **`test_process_project_task` (Updated):**
  - **Create Project:** We first create a `Project` in the database. This is necessary because `process_project` now expects a valid `project_id`.
  - **Run Task:** We call `process_project.delay()` with the project's ID.
  - **Verify Status:** We _refresh_ the project from the database (to get any changes made by the task) and then assert that its status has been updated to `COMPLETED`.
- **`test_process_project_task_failure` (NEW):**
  - **Simulate Error:** We call the process_project with an invalid project ID.
  - **`result.failed()`:** We use Celery's `result.failed()` method to check if the task failed. This relies on `task_eager_propagates = True` in the `celery_config`.
  - **Verify Status:** We check that the project's status has been updated to `ERROR` in the database.
- **`test_process_project_task_project_not_found`:** Test project not found case.

**Running the Tests:**

```bash
docker-compose run api pytest -v src/backend/tests/test_tasks
```

Run this to ensure that the project tests pass.

## 3. Frontend Integration - Get project list

Now, we can add some basic frontend integration. We'll modify the `/projects` page in your Next.js application to fetch and display the list of projects from the backend.

**Modify `src/frontend/app/projects/page.tsx`:**

```typescript
// src/frontend/app/projects/page.tsx
"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { projectsApi, ProjectSchema } from "@/lib/api"; // Import ProjectSchema
import { ThemeToggle } from "../../components/theme-toggle";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { Label } from "../../components/ui/label";
import {
    Card,
    CardHeader,
    CardContent,
    CardFooter,
  } from "@/components/ui/card";

export default function ProjectsPage() {
  const router = useRouter();
  const [isCreating, setIsCreating] = useState(false);
  const [topic, setTopic] = useState("");
  const [notes, setNotes] = useState("");
  const [projects, setProjects] = useState<ProjectSchema[]>([]); // Use ProjectSchema
  const [loading, setLoading] = useState(true); // Add loading state
  const [error, setError] = useState<string | null>(null); // Add error state


  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const project = await projectsApi.create({ topic, notes });
      setProjects([...projects, project]);
      setTopic("");
      setNotes("");
      setIsCreating(false);
    } catch (error) {
      console.error("Failed to create project:", error);
      // Set error state to display an error message.
      if (error instanceof Error) {
        setError(`Failed to create project: ${error.message}`);
      } else {
        setError(`Failed to create project: ${String(error)}`);
      }
    }
  };

  useEffect(() => {
    async function fetchProjects() {
      try {
        const fetchedProjects = await projectsApi.getAll();
        setProjects(fetchedProjects);
      } catch (error) {
        // Set error state to display an error message
        if (error instanceof Error) {
            setError(`Failed to fetch projects: ${error.message}`);
        }
        else {
            setError(`Failed to fetch projects ${String(error)}`);
        }
      } finally {
        setLoading(false);
      }
    }

    fetchProjects();
  }, []);

  return (
    <div className="container mx-auto py-8">
      <div className="mb-8 flex items-center justify-between">
        <h1 className="text-3xl font-bold">Projects</h1>
        <div className="flex items-center gap-4">
          <ThemeToggle />
          <Button onClick={() => setIsCreating(true)}>
            Create New Project
          </Button>
        </div>
      </div>

      {isCreating && (
        <Card>
          <CardHeader>
            <h2 className="text-xl font-semibold">Create Project</h2>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleCreateProject} className="space-y-4">
              <div>
                <Label htmlFor="topic">Topic</Label>
                <Input
                  type="text"
                  id="topic"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  required
                />
              </div>
              <div>
                <Label htmlFor="notes">Notes</Label>
                <Input
                  type="text"
                  id="notes"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                />
              </div>
            </form>
          </CardContent>
          <CardFooter>
           <div className="flex justify-end space-x-3">
              <Button variant="outline" onClick={() => setIsCreating(false)}>
                Cancel
              </Button>
              <Button type="submit">Create</Button>
           </div>
          </CardFooter>
        </Card>
      )}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">Error!</strong>
          <span className="block sm:inline"> {error}</span>
        </div>
      )}

    {loading ? (
        <div>Loading projects...</div>
      ) : (
        <Card>
          <ul className="divide-y divide-border">
            {projects.map((project) => (
              <li
                key={project.id}
                className="cursor-pointer p-4 hover:bg-accent hover:text-accent-foreground"
                onClick={() => router.push(`/projects/${project.id}`)}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-medium">
                      {project.name}
                    </h3>
                    <p className="text-sm text-muted-foreground">
                      Topic: {project.topic}
                    </p>
                  </div>
                  <div className="flex items-center space-x-4">
                    <span className="rounded-full bg-primary/10 px-2 py-1 text-sm text-primary">
                      {project.status}
                    </span>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </Card>
      )}
    </div>
  );
}
```

**Modify `src/frontend/lib/api.ts`:**
Add a new function called `getAll`.

```typescript
// src/frontend/lib/api.ts
import axios from "axios";
import type { Project, ProjectCreate, ProjectStatus } from "../types";

const getApiUrl = () => {
  if (typeof window === "undefined") {
    return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  } else {
    return "";
  }
};

const api = axios.create({
  baseURL: getApiUrl(),
});

export const projectsApi = {
  create: async (data: ProjectCreate): Promise<Project> => {
    const response = await api.post("/projects/", data);
    return response.data;
  },
  getStatus: async (projectId: string): Promise<ProjectStatus> => {
    const response = await api.get(`/projects/${projectId}/status`);
    return response.data;
  },
  getProject: async (projectId: string): Promise<Project> => {
    const response = await api.get(`/projects/${projectId}`);
    return response.data;
  },
  getAll: async (): Promise<Project[]> => {
    const response = await api.get("/projects/");
    return response.data;
  },
};

export type { Project as ProjectSchema, ProjectCreate, ProjectStatus };
```

Key Changes:

- **`useState` for `projects`:** We introduce a `projects` state variable to store the list of projects fetched from the API.
- **`useEffect` Hook:** We use the `useEffect` hook to fetch the projects when the component mounts. The empty dependency array (`[]`) ensures this effect runs only once.
- **`fetchProjects` Function:** This asynchronous function uses `projectsApi.getAll()` (which you'll need to add to `src/frontend/lib/api.ts`) to fetch the projects and update the `projects` state.
- **Error Handling**: Added basic error handling.
- **Loading State**: Added loading state.
- **`projectsApi.getAll()`:** Added a new function to get all of the projects.

**Run the Frontend:**

Make sure your backend is running, then start your frontend:

```bash
npm run dev --prefix src/frontend
```

You should now see the list of projects (initially empty, but you can create some) displayed on the `/projects` page. The "Create New Project" button and form should also work, and new projects should appear in the list.

This completes this part. You now have:

- Basic error handling and status updates within your `process_project` Celery task.
- Logging within your Celery task.
- A test case to verify task failure behavior.
- A frontend that can now list projects.

The next steps would involve fleshing out the `process_project` task with the actual video generation logic, adding retry mechanisms, and continuing to build out the frontend UI.
