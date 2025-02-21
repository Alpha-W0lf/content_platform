# Content Platform Development Guide - Part 2: PATCH Endpoint and Error Handling

This is Part 2 of 4 in the Content Platform Development Guide series:

- Part 1: Project Setup and Initial API/Model Tests
- Part 2 (Current): PATCH Endpoint and Error Handling
- Part 3: Task Testing and Request Logging
- Part 4: Task Error Handling and Frontend Integration

Okay, let's move on to the next part, which focuses on expanding the API tests to include the PATCH /projects/{id} endpoint and enhancing error handling, particularly around database operations.

# Content Platform Development and Testing Guide

This part builds on the previous part, adding tests for the `PATCH /projects/{id}` endpoint and enhancing error handling.

**Remember to always:**

- **Follow Best Practices:** Use clear naming conventions, write docstrings, keep functions small and focused, and adhere to PEP 8 style guidelines (enforced by your linters).
- **Maintainable Code:** Write code that is easy to understand, modify, and extend. Use comments where necessary to explain _why_ you're doing something, not just _what_.
- **Targeted Changes:** Make small, incremental changes. Commit frequently with descriptive commit messages.
- **Modularity and Extensibility:** Design your code with future features in mind. Think about how new functionality will be added and how existing components can be reused. Use dependency injection and clearly defined interfaces.
- **Test Driven Development**: Write tests before code.

## Task Tracking (v0.0 Foundation)

### Implemented ✓

- [x] API Tests (`src/backend/tests/test_api/test_projects.py`)
  - [x] `/projects/{id}` PATCH endpoint
    - [x] Basic field updates (topic, notes)
    - [x] Status updates
    - [x] Not found case
    - [x] Invalid status value
    - [x] Partial updates (only updating some fields)
    - [x] Edge cases (empty strings, etc.)
- [x] Error Handling (Enhancements)
  - [x] Database Operations (in `projects.py`)
    - [x] Connection errors (`OperationalError` handling _implemented_, direct automated testing deferred)
    - [x] Transaction errors (rollback on exception)

### In Progress 🚧

- [ ] API Tests (`src/backend/tests/test_api/test_projects.py`)

  - [ ] `/projects/{id}` PATCH endpoint
    - [ ] Error case coverage: `OperationalError` (Automated testing deferred; manual testing recommended for now. See Section 2.2 for details.)

- [ ] Error Handling (Enhancements)
  - [ ] Database Operations (in `projects.py`)
    - [ ] Constraint violations
  - [ ] API Endpoints
    - [ ] Conflict handling

### Next Steps 📋

1.  **Database Connection Error Test (Tricky):** Discuss strategy for testing `OperationalError`.
2.  **API Endpoint Enhancement:** Add conflict handling to the API endpoints.
3.  **Error Handling Documentation:** Document error handling patterns and best practices.

## 1. PATCH Endpoint Tests (Review)

You should already have comprehensive tests for the `PATCH` endpoint in `src/backend/tests/test_api/test_projects.py`, covering:

- Successful updates (topic, notes, status).
- Partial updates (only updating some fields).
- Not found (404) case.
- Invalid status value (422).
- Edge cases (empty strings).

Make sure these tests are present and passing. Refer to the complete `test_projects.py` file provided in the previous response if needed.

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

## 3. Next Steps (Checklist)

1.  **Review `projects.py`:** Ensure your API endpoints have the `OperationalError` handling as described above.
2.  **Run all tests:** `docker-compose run api pytest -v`
3.  **Manual Test:** perform a quick manual test to see error messages as described above.

Once you've done this, we can move on to the next part, which will cover Celery task testing and request logging middleware.
content_copy
download
Use code with caution.
Markdown

Key Changes in this guide:

Focus on PATCH endpoint tests: We're ensuring that the PATCH endpoint is thoroughly tested.

Enhanced Error Handling: Adding specific OperationalError handling to all API endpoints.

OperationalError Testing Strategy: Clearly outlining the options for testing database connection errors, with a recommendation to focus on logging for now.

Model testing is done: the model testing portion of the In Progress section is complete.
