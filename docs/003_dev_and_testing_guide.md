# Content Platform Development Guide - Part 3: Task Testing and Request Logging

This is Part 3 of 4 in the Content Platform Development Guide series:

- Part 1: Project Setup and Initial API/Model Tests
- Part 2: PATCH Endpoint and Error Handling
- Part 3 (Current): Task Testing and Request Logging
- Part 4: Task Error Handling and Frontend Integration

# Content Platform Development and Testing Guide

This part builds on the previous part, adding tests for Celery tasks and implementing request logging middleware.

**Remember to always:**

- **Follow Best Practices:** Use clear naming conventions, write docstrings, keep functions small and focused, and adhere to PEP 8 style guidelines (enforced by your linters).
- **Maintainable Code:** Write code that is easy to understand, modify, and extend. Use comments where necessary to explain _why_ you're doing something, not just _what_.
- **Targeted Changes:** Make small, incremental changes. Commit frequently with descriptive commit messages.
- **Modularity and Extensibility:** Design your code with future features in mind. Think about how new functionality will be added and how existing components can be reused. Use dependency injection and clearly defined interfaces.
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
  - [x] `/projects` POST endpoint
  - [x] `/projects/{id}` GET endpoint
  - [x] `/projects/{id}/status` GET endpoint
  - [x] `/projects` GET (list) endpoint
  - [x] `/projects/{id}` PATCH endpoint
- [x] Model Tests
  - [x] Project model
  - [x] Asset model
- [x] **Task Tests**

  - [x] Celery configuration tests
  - [x] Task execution tests (`test_task`)
  - [ ] Task error handling

- [x] Error Handling
  - [x] Database Operations
    - [x] Connection errors
    - [x] Transaction errors
  - [x] API Endpoints
    - [x] Input validation
    - [x] Not found handling

### In Progress 🚧

- [ ] **Task Tests** _<-- Focus here next_

  - [ ] Task error handling

- [ ] Error Handling (Enhancements)

  - [ ] API Endpoints
    - [ ] Conflict handling
  - [ ] Task Processing
    - [ ] Task failure handling _<-- Integrate with task tests_
    - [ ] Retry logic _<-- Add when you have retries_
    - [ ] Status updates

- [x] **Logging System**
  - [x] JSON logging setup
  - [x] Log levels configuration
  - [x] Request logging (middleware) _<-- Implement middleware_
  - [x] Error logging
  - [ ] Task logging _<-- Add when implementing tasks_

### Next Steps 📋

1.  **Complete Task Tests:** Focus on `process_project` task testing (basic execution, and error handling when you add more logic).
2.  **Implement Task Failure Handling and Status Updates:** Integrate error handling and status updates into the `process_project` task.
3.  **Add Celery Task Logging:**
4.  **Conflict Handling (API):** Consider adding conflict handling to your API (e.g., for duplicate project topics, if you add a unique constraint).
5.  **Start Connecting Frontend:** Once the backend is more solid, begin making API calls from your Next.js frontend.

## 1. Celery Task Tests

You've already set up the basic structure for Celery task tests in `src/backend/tests/test_tasks/test_project_tasks.py`. Review this file and ensure it's consistent with the example provided in previous responses:

```python
# src/backend/tests/test_tasks/test_project_tasks.py
import pytest
from src.backend.tasks.project_tasks import celery, test_task, process_project  # Import your tasks
from celery.result import AsyncResult

@pytest.fixture(scope="session")
def celery_config():
    return {
        'broker_url': 'memory://',  # Use in-memory broker for testing
        'result_backend': 'rpc://',  # Use RPC result backend for testing
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
    # For now, this will just check that the task runs without error.
    # As you implement project processing steps, you can add assertions
    # to verify the behavior.
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

**Key Points (Review):**

- **`celery_config` fixture:** Ensures tasks run synchronously during tests.
- **`@pytest.mark.celery`:** Marks tests that require the Celery app.
- **`test_task`:** A simple test to verify Celery is working.
- **`test_process_project_task`:** A placeholder for testing your main task. Right now, it just checks for successful execution (no errors). You'll add more assertions later as you implement the task's functionality.

**Running Celery Tests:**

```bash
docker-compose run api pytest -v src/backend/tests/test_tasks
```

## 2. Request Logging Middleware

Let's add middleware to your FastAPI application to automatically log all incoming requests. This is invaluable for debugging and monitoring.

**Modify `src/backend/main.py`:**

```python
# src/backend/main.py
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict
import time
import uuid

from fastapi import FastAPI, Request, Response  # Import Request and Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
import logging
from pythonjsonlogger import jsonlogger  # Import jsonlogger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup
    Instrumentator().instrument(app).expose(app)
    yield
    # Shutdown


app = FastAPI(
    title=settings.PROJECT_NAME, version=settings.API_VERSION, lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- JSON Logging Setup ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
# --- End JSON Logging Setup ---

# --- Request Logging Middleware ---
@app.middleware("http")
async def log_requests(request: Request, call_next):
    idem = uuid.uuid4()
    logger.info(f"Request started: {request.method} {request.url.path} id={idem}")

    start_time = time.time()
    response: Response = await call_next(request)  # Call the next middleware/route handler
    end_time = time.time()

    process_time = (end_time - start_time) * 1000
    formatted_process_time = f"{process_time:.2f}"

    logger.info(
        f"Request finished: {request.method} {request.url.path} id={idem}",
        extra={
            "http.status_code": response.status_code,
            "http.method": request.method,
            "http.path": request.url.path,
            "http.duration": formatted_process_time,
        },
    )

    return response
# --- End Request Logging Middleware ---

# Include routers
app.include_router(projects.router, prefix="/api/v1", tags=["projects"])


@app.get("/health")
async def health_check() -> Dict[str, str]:
    return {"status": "healthy"}

```

Key Changes:

- **Import `Request` and `Response`:** Added `from fastapi import Request, Response`.
- **`log_requests` Middleware:**

  - `@app.middleware("http")`: This decorator registers the function as middleware that will be executed for every HTTP request.
  - `async def log_requests(request: Request, call_next):`: The middleware function takes the `Request` object and a `call_next` function (which calls the next middleware or the route handler).
  - `idem = uuid.uuid4()`: Generates a unique ID for each request. This is very useful for tracing requests through your logs.
  - `logger.info(...)`: Logs the start of the request, including the method (GET, POST, etc.) and the URL path.
  - `start_time = time.time()`: Records the start time.
  - `response: Response = await call_next(request)`: This is _crucial_. It calls the next middleware in the chain (or the final route handler if this is the last middleware). The `await` is important because the handler might be asynchronous.
  - `end_time = time.time()`: Records the end time.
  - `process_time = ...`: Calculates the processing time in milliseconds.
  - `logger.info(...)`: Logs the completion of the request, including the status code and the processing time. We use the `extra` argument to add structured data to the log message, which is ideal for JSON logging.
  - `return response`: return the response.

- **JSON Logging**: confirmed that the JSON logging setup is complete.

**How to Verify the Middleware:**

1.  Restart your FastAPI server (`docker-compose up --build`).
2.  Make some requests to your API endpoints (e.g., create a project, get project status).
3.  Observe the logs in your terminal (where Docker Compose is running). You should see JSON log entries for each request, including the start and end times, method, path, status code, and processing time.

Example Log Output (you'll see something like this):

```json
{"asctime": "2024-02-17 10:30:00,123", "levelname": "INFO", "name": "src.backend.main", "message": "Request started: POST /api/v1/projects/ id=a1b2c3d4-e5f6-7890-1234-567890abcdef"}
{"asctime": "2024-02-17 10:30:00,456", "levelname": "INFO", "name": "src.backend.main", "message": "Request finished: POST /api/v1/projects/ id=a1b2c3d4-e5f6-7890-1234-567890abcdef", "http.status_code": 201, "http.method": "POST", "http.path": "/api/v1/projects/", "http.duration": "333.23"}
```

This structured logging is extremely valuable for:

- **Debugging:** Quickly identify slow requests or errors.
- **Monitoring:** Track API performance and usage patterns.
- **Auditing:** Keep a record of all requests.

This completes this part. You now have:

- Working Celery task tests (basic).
- Request logging middleware in your FastAPI application.

The next part will involve integrating error handling and status updates into your Celery task, and starting to connect the frontend.
