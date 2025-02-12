# Progress Tracking

- [ ] **II. Detailed Test Plan (Backend)**
  - [ ] **A. test_projects.py (API Endpoints)**
    - [ ] Fixtures: `setup_database`, `db_session`, `client`
    - [ ] Tests for `POST /projects`: `test_create_project_success`, `test_create_project_missing_topic`, `test_create_project_invalid_topic_type`, `test_create_project_invalid_notes_type`
    - [ ] Tests for `GET /projects/{project_id}/status`: `test_get_project_status_valid_id`, `test_get_project_status_invalid_id`, `test_get_project_status_invalid_id_format`
    - [ ] Tests for `GET /projects`: `test_list_projects_empty`, `test_list_projects_with_data`
    - [ ] Tests for `GET /health`: `test_health_check`
  - [ ] **B. test_tasks.py (Celery Tasks - Basic)**
    - [ ] Fixtures: `celery_app`
    - [ ] Tests: `test_test_task`

Okay, let's create a detailed testing plan for the current state of your project. This plan focuses on what you've already built, covering the backend API endpoints and basic Celery setup. We'll use pytest, httpx, and leverage FastAPI's testing utilities.

I. Overall Testing Strategy

Type of Tests: Primarily integration tests (testing the interaction between different parts of your application, like the API and the database) and some unit tests (testing individual functions/classes in isolation). We'll defer more complex end-to-end (E2E) tests involving the frontend until later.

Tools:

pytest: Test runner and framework.

httpx: Asynchronous HTTP client for making requests to your API.

pytest-asyncio: Provides support for testing async code with pytest.

FastAPI's TestClient: A convenient way to simulate requests to your FastAPI application within tests (although we'll primarily use httpx for a more realistic approach).

Database Fixtures: We'll use pytest fixtures to set up a clean database state for each test (create tables, potentially seed with initial data, and then drop tables after the test).

Test organization: We will place the test files in the backend.

src/backend/tests/test_api/test_projects.py

II. Detailed Test Plan (Backend)

A. test_projects.py (API Endpoints)

Fixtures:

setup_database: (Function-scoped)

Create all database tables before each test function using Base.metadata.create_all.

Drop all tables after each test function using Base.metadata.drop_all. This ensures a clean slate for each test.

db_session: (Function-scoped)

Provide an AsyncSession instance for each test function, allowing interaction with the database.

Automatically close the session after each test.

client: (Module-scoped – can be function-scoped if needed)

Create an httpx.AsyncClient instance, configured to talk to your FastAPI application. Using app=app and base_url="http://test" is the standard way to do this with FastAPI.

Tests for POST /projects:

test_create_project_success:

Send a valid request body: {"topic": "Test Topic", "notes": "Optional notes"}.

Assert status code: 200.

Assert response body:

Contains a UUID for the id.

topic and notes match the request.

status is "CREATED".

name is initially null.

(Optional, but recommended): Directly query the database to confirm the project was created.

test_create_project_missing_topic:

Send a request with a missing topic: {}.

Assert status code: 422.

Assert response body indicates the missing field error (check for a specific error message).

test_create_project_invalid_topic_type:

Send request with wrong data type.

Assert status code: 422.

Assert response body indicates the error.

test_create_project_invalid_notes_type:

Send a request with an invalid notes type (e.g., a number).

Assert status code: 422.

Assert a specific error message in the response.

Tests for GET /projects/{project_id}/status:

test_get_project_status_valid_id:

First, create a project using a POST request (you can reuse the logic from test_create_project_success).

Get the project_id from the creation response.

Send a GET request to /projects/{project_id}/status.

Assert status code: 200.

Assert response body: {"status": "CREATED"} (or whatever the initial status is).

test_get_project_status_invalid_id:

Send a GET request with a non-existent UUID.

Assert status code: 404.

Assert response body: {"detail": "Project not found"}.

test_get_project_status_invalid_id_format:

Send GET request with wrong id data type.

Assert status code: 422 or 404.

Tests for GET /projects:

test_list_projects_empty:

Send a GET request to /projects.

Assert status code: 200.

Assert response body: [] (an empty list).

test_list_projects_with_data:

Create multiple projects using POST requests.

Send a GET request to /projects.

Assert status code: 200.

Assert response body is a list with the correct number of projects.

Assert that each project in the list has the expected data (ID, topic, status, etc.).

Tests for GET /health:

test_health_check:

Send a GET request to /health.

Assert status code: 200.

Assert response body is {"status": "OK"}

B. test_tasks.py (Celery Tasks - Basic)

Fixtures:

celery_app: (Module or session-scoped)

Configure Celery for testing. The key here is usually to set task_always_eager = True. This makes Celery tasks run synchronously within your tests, so you don't have to deal with asynchronous task execution and results during testing. This is set in the celery_config.py file.
```python
#src/backend/tests/test_tasks.py
import pytest
from src.backend.tasks.project_tasks import celery, test_task

@pytest.fixture(scope="session")
def celery_config():
    return {
      'broker_url': 'memory://', # Use in-memory broker for testing.
      'result_backend': 'rpc://', #Use RPC result backend for testing.
        'task_always_eager': True,  # Run tasks synchronously
        'task_eager_propagates': True,
    }

@pytest.mark.celery
def test_test_task(celery_app):
    result = test_task.delay(2, 3)
    assert result.get() == 5
    assert result.successful()

```
content_copy
download
Use code with caution.

Tests:

test_test_task:

Call test_task.delay(4, 4) (or whatever arguments your task takes).

Assert result.get() == 8 (check the return value).

Assert result.successful() is True.

III. Running the Tests

From the command line (within the api container):

docker-compose run api pytest
content_copy
download
Use code with caution.
Bash

Or, if you want to run a specific test file:

docker-compose run api pytest src/backend/tests/test_api/test_projects.py
content_copy
download
Use code with caution.
Bash

IV. Important Considerations

Test Database: It's highly recommended to use a separate database for testing. This prevents your tests from interfering with your development or production data.

You can configure a separate DATABASE_URL in your .env file (e.g., TEST_DATABASE_URL).

Then, in your src/backend/tests/conftest.py, you can override the settings.DATABASE_URL during testing:

# src/backend/tests/conftest.py
import pytest
from src.backend.core.config import settings

@pytest.fixture(scope="session", autouse=True)
def override_settings():
    settings.DATABASE_URL = settings.TEST_DATABASE_URL  # Assuming you have TEST_DATABASE_URL
    yield
    # Optionally reset to original value after tests (usually not needed)
content_copy
download
Use code with caution.
Python

Mocking: As you progress to v0.1 and beyond, you'll need to use mocking extensively. Mocking allows you to replace external dependencies (like the HeyGen API or Gemini Pro API) with controlled substitutes during testing. This makes your tests faster, more reliable, and prevents you from making unnecessary external API calls during testing. Libraries like unittest.mock (or pytest-mock, which integrates well with pytest) are essential for this.

Code Coverage: Consider using a code coverage tool (like coverage.py or pytest-cov) to measure how much of your code is actually being executed by your tests. This helps identify gaps in your testing.

This detailed plan should give you a solid foundation for testing the current state of your project. Remember, testing is an investment that pays off significantly in the long run!