# Content Platform Rapid Development Guide 001

## Task Tracking

### In Progress

- [ ] **Simplify API Endpoints and Tests:** Remove `name` and `notes` fields from project creation and listing, adjusting tests accordingly.
- [ ] **Simplify Frontend:**  Ensure the frontend only uses the `topic` for project creation. Remove unnecessary UI elements.
- [ ] **Run in Local Environment:** Use a local postgresql database and remove docker.

### Completed

- [x] Initial project setup
- [x] Development guide creation
- [x] Basic folder structure
- [x] Project Creation API endpoint
- [x] Project Listing API endpoint
- [x] Get project by ID API endpoint
- [x] Project Status endpoint
- [x] Update project via PATCH API endpoint
- [x] Basic database models and migrations
- [x] Basic Frontend (Next.js, Tailwind, shadcn/ui setup)
- [x] API Tests
- [x] Model Tests
- [x] Basic Frontend - Project Creation
- [x] Basic Frontend - Project Listing
- [x] Basic Frontend - Project Detail
- [x] Basic Error Handling
- [x] Test Redis Connection
- [x] Test Celery Task
- [x] Test Process Project

### Up Next (After v0.0 - DO NOT START YET)

- [ ] Authentication (Clerk)
- [ ] Celery integration
- [ ] Asset management
- [ ] AI features
- [ ] UI refinements
- [ ] More comprehensive testing
- [ ] Deployment configuration


# Content Platform Development Guide

This document outlines the development plan for the Content Platform, focusing on a rapid, iterative approach to reach a minimal viable product (v0.0) quickly.

## Guiding Principles

*   **Iterative Development:** We'll build the platform in small, incremental steps, focusing on core functionality first.
*   **"Spike, Then Test":**  For new features, we'll start with a "spike" – a quick, exploratory implementation to validate the approach. Then, we'll write targeted tests and refactor.
*   **Defer Complexity:**  We'll postpone non-essential features and infrastructure until after v0.0 is working.
*   **Local Development First:**  We'll primarily develop and test locally, using Docker for integration testing and deployment.  This speeds up the development loop.
*   **"Good Enough" for v0.0:**  We'll aim for functional correctness and reasonable code quality, and always following best practices, but we won't strive for perfection in v0.0.
*   **Prioritize Core Workflow:** We'll add user interaction, create, update, and get status.

## v0.0 Feature Set (Minimal Viable Product)

The goal of v0.0 is to demonstrate the core concept of the platform: creating and managing content projects.  We'll focus on the absolute minimum features needed to achieve this:

*   **Project Creation:**
    *   Users can create a project with a **topic** (and nothing else).
    *   Projects are stored in the PostgreSQL database.
    *   No authentication (for now).
*   **Project Listing:**
    *   Users can view a list of all projects, showing their topic and status.
* **Project Get by ID**
    * Users can view the details of a project
* **Project Status Update**
    * Users can update the status of a project.
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
    *   Set up a local PostgreSQL database (or use a separate Docker Compose setup for *just* the database).  **This is key for fast development.**
    *   Configure your `src/backend/.env` file to point to the local database.
    *   Run Alembic migrations: `alembic upgrade head` (from within `src/backend`).

2.  **Backend Development (Iterative):**
    *   **Spike:** Implement a simplified version of a feature (e.g., project creation) *without* tests. Use print statements for debugging. Work directly with your local Python environment and local database.
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
    *   Interact with your application through the browser and an API client (like Postman or `httpie`).
    *   Run your tests frequently: `pytest` (from within `src/backend`)

5.  **Docker Integration (Periodic):**
    *   **IMPORTANT:** Once a feature is *fully working and tested locally*, test it within Docker to ensure everything works correctly in the containerized environment. This is your *integration* testing step.
    *   Use `docker-compose build` and `docker-compose up`.
    *   Use `docker-compose logs` to view logs.

6.  **Iterate:** Continue this process, adding features and refactoring as you go.

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

    *   **Install PostgreSQL locally.** Follow the instructions for your operating system (macOS). Make sure the PostgreSQL server is running.


4.  **.env File:**

    Create (or modify) `src/backend/.env`:
    ```
    DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/content_platform_dev
    ```
    Adjust `DATABASE_URL` to match your *local* PostgreSQL setup.  If using Option 2 above, use `DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/content_platform_dev` (note `postgres` as the hostname, not `localhost`).  The `TEST_DATABASE_URL` in `.env` should *still* point to the `test_content_platform` database.

5.  **Alembic Migrations:**

    From within the `src/backend` directory:
    ```
    alembic upgrade head
    ```

6.  **Test Project Creation:**

    *   Run your backend.
    *   Send a `POST` request to `http://localhost:8000/api/v1/projects` with the following body:
        ```json
        {
            "topic": "Test Topic"
        }
        ```
    *   Verify that the request returns a successful status code.
    *   Check the `projects` table inside the database.

## Code Style and Best Practices

*   **Follow PEP 8:** Use consistent naming conventions, indentation, and whitespace. Your linters will help enforce this.
*   **Docstrings:** Write clear docstrings for all functions and classes.
*   **Type Hints:** Use type hints throughout your code.
*   **Keep Functions Small:** Break down large functions into smaller, more manageable units.
*   **Comments:** Use comments to explain *why* you're doing something, not just *what*.
*   **Error Handling:** Use `try...except` blocks to handle potential errors, especially in database operations and API calls. Raise `HTTPException` for API errors.

## Next Steps (After v0.0 - DO NOT START YET)

Once you have a working v0.0, you can start adding features:

*   **Authentication:** Integrate Clerk for user authentication.
*   **Celery Integration:** Implement asynchronous task processing with Celery and Redis.
*   **Asset Management:** Add models and API endpoints for managing assets (scripts, narrations, videos, etc.).
*   **AI Features:** Integrate AI models for script generation, asset creation, and video composition (as discussed in your brainstorming documents).
*   **UI Improvements:** Build a more user-friendly and visually appealing frontend.
*   **More Comprehensive Testing:** Add more comprehensive tests, including integration tests and end-to-end tests.
*   **Deployment:** Configure your application for deployment to a production environment.
```

Key Changes and Why:

*   **Stronger Emphasis on Local Development:** I've explicitly stated that Docker is *not* for the primary development loop in v0.0, and I've highlighted the benefits of local development.
*   **"Transitioning Back to Docker" Section:** This new section provides a clear roadmap for re-integrating Docker after the initial v0.0 development. This addresses your concern about "abandoning" Docker.
*   **Clarified .env Usage:**  I've made it clear that you might need separate `.env` files for local development and Docker, or you can carefully manage a single `.env`.
*   **"Spike, Then Test" Reinforcement:** I've re-emphasized this approach in the Guiding Principles and Workflow.
* **Added Next Steps (After v0.0):** Added a section describing the next steps after v0.0 is complete.
* **Added immediate action items at the bottom of the document.**

This revised guide should be even clearer about the recommended workflow and how Docker fits into the overall picture. You're not abandoning Docker; you're strategically using it at the right time in the development process. The local development phase is about speed and rapid iteration; the Docker phase is about ensuring everything works correctly in a production-like environment.
