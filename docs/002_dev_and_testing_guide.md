```markdown
# Content Platform Development Guide - Part 2: PATCH Endpoint and Error Handling

This is Part 2 of 4 in the Content Platform Development Guide series:

- Part 1: Project Setup and Initial API/Model Tests
- Part 2 (Current): PATCH Endpoint and Error Handling
- Part 3: Task Testing and Request Logging
- Part 4: Task Error Handling and Frontend Integration

# Content Platform Development and Testing Guide

This part builds on the previous part, adding tests for the `PATCH /projects/{id}` endpoint and enhancing error handling.

**Remember to always:**

- **Follow Best Practices:** Use clear naming conventions, write docstrings, keep functions small and focused, and adhere to PEP 8 style guidelines (enforced by your linters).
- **Maintainable Code:** Write code that is easy to understand, modify, and extend. Use comments where necessary to explain _why_ you're doing something, not just _what_.
- **Targeted Changes:** Make small, incremental changes. Commit frequently with descriptive commit messages.
- **Modularity and Extensibility:** Design your code with future features in mind. Think about how new functionality will be added and how existing components can be reused. Use dependency injection and clearly defined interfaces.
- **Test Driven Development:** Write tests before code.

## Task Tracking (v0.0 Foundation)

### Implemented ✓

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
- [x] Model Tests
  - [x] Project model
  - [x] Asset model
- [x] Error Handling
  - [x] Database Operations (in `projects.py`)
    - [x] Connection errors (`OperationalError` handling _implemented_, direct automated testing deferred)
    - [x] Transaction errors (rollback on exception)
  - [x] API Endpoints
    - [x] Input validation
    - [x] Not found handling
  - [x] Initial try/except blocks in endpoints

### In Progress 🚧

- [ ] API Tests (`src/backend/tests/test_api/test_projects.py`)

  - [ ] `/projects/{id}` PATCH endpoint
    - [ ] Basic field updates (topic, notes)
    - [ ] Status updates
    - [ ] Not found case
    - [ ] Invalid status value
    - [ ] Partial updates (only updating some fields)
    - [ ] Edge cases (empty strings, etc.)
    - [ ] Error case coverage: `OperationalError` (Automated testing deferred; manual testing recommended for now. See Section 2.2 for details.)

- [ ] Error Handling (Enhancements)
  - [ ] Database Operations (in `projects.py`)
    - [ ] Constraint violations
  - [ ] API Endpoints
    - [ ] Conflict handling

### Next Steps 📋

1.  **Review `projects.py`:** Ensure your API endpoints have the `OperationalError` handling as described above.
2.  **Run all tests:** `docker-compose run api pytest -v`
3.  **API Endpoint Enhancement:** Add conflict handling to the API endpoints.
4.  **Error Handling Documentation:** Document error handling patterns and best practices.
5. **Constraint Violations:** Discuss strategy for testing `OperationalError`.

## 1. PATCH Endpoint Tests (TDD Approach)

In this section, we'll implement the `PATCH /projects/{id}` endpoint using a Test-Driven Development (TDD) approach. This means we'll write the tests *before* writing the corresponding endpoint code.  This helps ensure that our endpoint behaves correctly and handles all expected cases, including errors.

We'll start by creating test cases in `src/backend/tests/test_api/test_projects.py` that cover the following scenarios:

*   **Successful Updates:**
    *   Updating the `topic`.
    *   Updating the `notes`.
    *   Updating the `status` (to valid values).
    *   Updating multiple fields at once.
*   **Partial Updates:**
    *   Updating *only* the `topic`.
    *   Updating *only* the `notes`.
    *   Updating *only* the `status`.
*   **Error Cases:**
    *   **Not Found (404):**  Trying to update a project with an ID that doesn't exist.
    *   **Invalid Status Value (422):**  Trying to update the `status` to an invalid enum value.
    *   **Invalid Data Types (422):** Sending invalid data types (e.g., a number for the topic).
    *   **Empty Strings (and other edge cases):** Testing with empty strings for `topic` and `notes`.
    *   **Database Errors:** As discussed below, we'll focus on the *structure* of error handling for now, deferring full automated testing of `OperationalError`.

We will write tests to explicitly check for the correct status code AND return value from the backend.

**Example Test Structure (Conceptual - you'll fill in the details):**

```python
@pytest.mark.asyncio
async def test_update_project_topic(client: AsyncClient, db_session: AsyncSession):
    # 1. Create a project in the database (Arrange)

    # 2. Send a PATCH request with updated data (Act)

    # 3. Assert the response status code and content (Assert)

    # 4.  (Optional but recommended) Fetch the project from the
    #     database and assert that the changes were persisted.
```

You'll create separate test functions for each of the scenarios listed above, following this pattern.  We'll start with the "Successful Updates" and "Partial Updates" cases, then move on to the "Error Cases."

## 2. Enhanced Error Handling and Testing

### 2.1. `OperationalError` Handling (Review)

You've already added `OperationalError` handling to your API endpoints in `src/backend/api/routers/projects.py`. This is excellent. Review the code to ensure:

- You're catching `sqlalchemy.exc.OperationalError` in a `try...except` block _around your database operations_.
- You're rolling back the transaction (`await db.rollback()`).
- You're logging the error with `logger.error`, including `exc_info=True`.
- You're raising an `HTTPException` with a `500` status code and a user-friendly message (e.g., "Database connection error").

### 2.2. Testing `OperationalError` (The Challenge)

As we discussed, directly testing `OperationalError` with `httpx.AsyncClient` and your in-memory test database is difficult. Here are the best approaches, ordered from simplest to most complex:

**Option 1: Focus on Logging (Simplest - Recommended for Now):**

- **Don't try to _force_ a connection error in your unit tests.** It's too complex and brittle for this stage.
- **Focus on verifying that your _error handling code is present and correctly structured_.** You've already done this by ensuring the `try...except` blocks, logging, and `HTTPException` are in place.
- **Add a simple _manual_ test:**
  1.  Temporarily modify your `DATABASE_URL` in your `.env` file to point to a _non-existent_ database (e.g., change the database name to something that doesn't exist).
  2.  Run your application _outside_ of the test suite (just start it with `docker-compose up`).
  3.  Try to make a request to an API endpoint.
  4.  Verify that you see a "Database connection error" message in the response and a detailed error log in your console output (because you're using structured logging).
  5.  **Change the `DATABASE_URL` back to the correct value!**
- This approach doesn't give you automated test coverage of the connection error, but it gives you _confidence_ that the error handling logic will work as expected in a real-world scenario.

**Option 2: Mocking (More Advanced):**

- Use the `unittest.mock` library (or `pytest-mock`) to replace the database connection with a mock object.
- Configure the mock to raise an `OperationalError` when you call a database operation (e.g., `await db.execute(...)`).
- This allows you to test the error handling code _within_ your unit tests.
- **Example (Conceptual - requires `pytest-mock`):**

  ```python
  import pytest
  from sqlalchemy.ext.asyncio import AsyncSession
  from sqlalchemy.exc import OperationalError
  from unittest.mock import AsyncMock  # Use AsyncMock for async functions

  @pytest.mark.asyncio
  async def test_create_project_database_error(client: AsyncClient, mocker):
      # Mock the db.execute method to raise an OperationalError
      mock_execute = AsyncMock(side_effect=OperationalError("Simulated DB Error", None, None))
      mocker.patch("src.backend.core.database.AsyncSession.execute", mock_execute) #Correct path

      data = {"topic": "Test Topic", "notes": "Test Notes"}
      response = await client.post("/api/v1/projects/", json=data)

      assert response.status_code == 500
      assert response.json() == {"detail": "Database connection error"}
      mock_execute.assert_called_once()  # Verify that the mocked method was called

  ```

  - You would need to adapt this to mock the `db.add`, `db.commit`, etc., methods as appropriate.
  - This approach is more complex, but it provides true unit test coverage of your error handling.

**Option 3: Separate Integration/System Tests (Most Complex):**

- Create a completely separate set of tests that run against a _real_ (but disposable) PostgreSQL database.
- These tests would be run _outside_ of your main `pytest` run (e.g., in a separate CI/CD job).
- You could use a tool like Docker Compose to start a temporary PostgreSQL instance for these tests.
- You could then deliberately disrupt the database connection (e.g., stop the PostgreSQL container) to trigger the `OperationalError`.

**Recommendation:**

For v0.0, I strongly recommend sticking with **Option 1 (Focus on Logging)**. It's the simplest and most pragmatic approach for now. You can add mocking or separate integration tests later as your project matures. The key is to have the error handling logic _in place_, even if you're not exhaustively testing every possible database error scenario at this stage.

### 2.3. Testing Constraint Violations

Besides `OperationalError`, we also need to ensure our database constraints are enforced.  This includes:

*   **Enum Validation:** The `status` field in the `Project` model can only accept values defined in the `ProjectStatus` enum.  We should test that attempting to update the `status` to an invalid value results in an appropriate error (likely a 422 Unprocessable Entity).
* **Data Type Validation**: The database will enforce types based on the model.

We can test these constraints by:

1.  Creating a valid `Project` in the database.
2.  Sending a `PATCH` request with an invalid value (e.g., an invalid `status` or incorrect data type).
3.  Asserting that the response status code is 422 (or another appropriate error code).
4. **Checking the Database State:** Verifying the data has not been changed.

## 3. Next Steps (Checklist)

1.  **Review `projects.py`:** Ensure your API endpoints have the `OperationalError` handling as described above.
2.  **Run all tests:** `docker-compose run api pytest -v`

Once you've done this, we can move on to the next part, which will cover Celery task testing and request logging middleware.
```