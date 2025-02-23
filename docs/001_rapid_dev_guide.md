```markdown
# Content Platform Development Guide

This document outlines the development plan for the Content Platform, focusing on a rapid, iterative approach to reach a minimal viable product (v0.0) quickly.

## Guiding Principles

*   **Iterative Development:** We'll build the platform in small, incremental steps, focusing on core functionality first.
*   **"Spike, Then Test":**  For new features, we'll start with a "spike" – a quick, exploratory implementation to validate the approach. Then, we'll write targeted tests and refactor.
*   **Defer Complexity:**  We'll postpone non-essential features and infrastructure until after v0.0 is working.
*   **Local Development First:**  We'll primarily develop and test locally, using Docker for integration testing and deployment.
*   **"Good Enough" for v0.0:**  We'll aim for functional correctness and reasonable code quality, but we won't strive for perfection in v0.0.
*   **Prioritize Core Workflow:** We'll add user interaction, create, update, and get status.

## v0.0 Feature Set (Minimal Viable Product)

The goal of v0.0 is to demonstrate the core concept of the platform: creating and managing content projects.  We'll focus on the absolute minimum features needed to achieve this:

*   **Project Creation:**
    *   Users can create a project with a **topic** (and nothing else).
    *   Projects are stored in the PostgreSQL database.
    *   No authentication (for now).
*   **Project Listing:**
    *   Users can view a list of all projects, showing their topic and status.
*   **Project Status:**
    *   Projects have a status (CREATED, PROCESSING, COMPLETED, ERROR).
    *   Initially, status changes will be done via direct API calls (no actual processing).
*   **Basic Frontend:**
    *   A simple Next.js frontend to interact with the API (list projects, create projects).
*   **NO Celery/Redis (for now):** Asynchronous task processing is deferred.
*   **NO Asset Management (for now):** No file uploads, storage, or relationships.
* **Minimal Error Handling** Add basic error handling for database interactions and API endpoint.
* **Basic API Documentation:** Create basic documentation for the API endpoints.

## Tech Stack

*   **Backend:** FastAPI, SQLAlchemy, PostgreSQL
*   **Frontend:** Next.js, Tailwind CSS, shadcn/ui
*   **Database:** PostgreSQL
*   **Testing:** pytest, httpx (for API tests)
*   **Code Quality:** black, isort, flake8, mypy (with relaxed settings initially)
*   **Containerization:** Docker, Docker Compose (for integration testing and deployment)

## Development Workflow

1.  **Local Setup:**
    *   Create a Python virtual environment.
    *   Install backend dependencies: `pip install -r src/backend/requirements.txt`
    *   Set up a local PostgreSQL database (or use a separate Docker Compose setup for *just* the database).
    *   Configure your `src/backend/.env` file to point to the local database.
    *   Run Alembic migrations: `alembic upgrade head` (from within `src/backend`).

2.  **Backend Development (Iterative):**
    *   **Spike:** Implement a simplified version of a feature (e.g., project creation) *without* tests. Use print statements for debugging.
    *   **Test:** Write *targeted* tests for the core functionality.
    *   **Refactor:** Improve the code structure, add error handling, and add docstrings.
    *   **Repeat:** Move on to the next feature.

3.  **Frontend Development (Minimal UI):**
    *   Create basic Next.js pages to interact with your API.
    *   Use shadcn/ui components for consistent styling.
    *   Keep the UI as simple as possible.

4.  **Local Testing:**
    *   Run your FastAPI server locally: `uvicorn src.backend.main:app --reload`
    *   Run your Next.js frontend locally: `npm run dev` (from within `src/frontend`)
    *   Interact with your application through the browser and API client.
    *   Run your tests frequently: `pytest` (from within `src/backend`)

5.  **Docker Integration (Periodic):**
    *   Once a feature is working locally, test it within Docker to ensure everything works correctly in the containerized environment.
    *   Use `docker-compose build` and `docker-compose up`.
    *   Use `docker-compose logs` to view logs.

6. **Add PATCH endpoint**:
    * Implement the PATCH endpoint
    * Add error handling to the endpoint
    * Write tests for the endpoint

7. **Add Task Testing and Logging**:
    * Write tests for celery tasks.
    * Add request logging middleware.

8. **Add Task Error Handling and Frontend Integration**:
    * Add task error handling, and status updates to Celery task.
    * Add logging to the Celery task.
    * Test task failure handling.
    * Connect the Next.js frontend to the backend.

9.  **Iterate:** Continue this process, adding features and refactoring as you go.

## Detailed Steps (Initial Setup)

This section expands on the initial setup steps:

1.  **Virtual Environment:**
    *   From your project's root directory:
        ```bash
        cd src/backend
        python3 -m venv .venv
        source .venv/bin/activate  # or .venv\Scripts\activate on Windows
        ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Local PostgreSQL:**

    *   **Option 1 (Recommended): Install PostgreSQL locally.** Follow the instructions for your operating system (macOS, Windows, Linux). Make sure the PostgreSQL server is running.

    *   **Option 2 (Docker - Separate Compose file):**

        Create a `docker-compose-db.yml` file in your project root:

        ```yaml
        version: '3.8'
        services:
          postgres:
            image: postgres:15
            ports:
              - "5432:5432"
            environment:
              POSTGRES_USER: user
              POSTGRES_PASSWORD: password
              POSTGRES_DB: content_platform_dev  # IMPORTANT: Different name
            volumes:
              - postgres_data_dev:/var/lib/postgresql/data

        volumes:
          postgres_data_dev:

        ```

        Run `docker-compose -f docker-compose-db.yml up -d`

4. **.env File:**

    Create (or modify) `src/backend/.env`:
    ```
    DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/content_platform_dev
    ```
    Adjust `DATABASE_URL` to match your local PostgreSQL setup.  If using Option 2 above, use `DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/content_platform_dev` (note `postgres` as the hostname, not `localhost`).
    The `TEST_DATABASE_URL` should still point to the `test_content_platform` database, as that is used by the testing environment.

5. **Alembic Migrations:**

    From within the `src/backend` directory:
        ```
        alembic upgrade head
        ```

6. **Test Project Creation**:

    * Run your backend.
    * Send a POST request to `http://localhost:8000/api/v1/projects` with the following body:
    ```json
    {
        "topic": "Test Topic",
        "name": "Test Name",
        "notes": "Test Notes"
    }
    ```
    * Verify that the request returns a successful status code.
    * Check the `projects` table inside the database.

## Code Style and Best Practices

*   **Follow PEP 8:** Use consistent naming conventions, indentation, and whitespace. Your linters will help enforce this.
*   **Docstrings:** Write clear docstrings for all functions and classes.
*   **Type Hints:** Use type hints throughout your code.
*   **Keep Functions Small:** Break down large functions into smaller, more manageable units.
*   **Comments:** Use comments to explain *why* you're doing something, not just *what*.
*   **Error Handling:** Use `try...except` blocks to handle potential errors, especially in database operations and API calls. Raise `HTTPException` for API errors.

## Next Steps (After v0.0)

Once you have a working v0.0, you can start adding features:

*   **Authentication:** Integrate Clerk for user authentication.
*   **Celery Integration:** Implement asynchronous task processing with Celery and Redis.
*   **Asset Management:** Add models and API endpoints for managing assets (scripts, narrations, videos, etc.).
*   **AI Features:** Integrate AI models for script generation, asset creation, and video composition (as discussed in your brainstorming documents).
*   **UI Improvements:** Build a more user-friendly and visually appealing frontend.
*   **More Robust Testing:** Add more comprehensive tests, including integration tests and end-to-end tests.
*   **Deployment:** Configure your application for deployment to a production environment.

This guide provides a clear roadmap for building your Content Platform. Remember to focus on small, incremental steps, and don't be afraid to refactor and improve your code as you go. The key is to get a working version up and running quickly, and then iterate based on feedback (even if it's just your own feedback).
```

This `development_guide.md` file now becomes your central document.  You can update it as you make progress and refine your plans. You no longer need the separate numbered guide files. Good luck building v0.0!
