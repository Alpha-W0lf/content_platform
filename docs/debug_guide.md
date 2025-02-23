Let’s dive into debugging this issue step-by-step based on the `conftest.py` file and the logs you’ve provided. The errors indicate two main problems: a `ValueError` related to the `REDIS_PASSWORD` environment variable and a `sqlalchemy.exc.ArgumentError` due to an unparsable SQLAlchemy URL. I’ll address both, focusing on the root causes and how to resolve them.

### Problem 1: `REDIS_PASSWORD` Environment Variable Missing
The logs show that when `celeryconfig.py` is loaded (likely imported somewhere in your test suite or app initialization), it raises:

```
ValueError: REDIS_PASSWORD environment variable is required
```

This happens because `validate_env("REDIS_PASSWORD", str)` in `celeryconfig.py` expects `REDIS_PASSWORD` to be set, and if it’s not, it throws an exception. The logs confirm this with `validate_env: REDIS_PASSWORD=None`.

#### Analysis
- In your `conftest.py`, the `setup_test_env` fixture attempts to set `REDIS_PASSWORD`:
  ```python
  redis_password = settings.REDIS_PASSWORD or "testpassword"
  os.environ["REDIS_PASSWORD"] = redis_password
  ```
- However, this fixture might not be executing before `celeryconfig.py` is imported. Pytest fixtures are only applied when tests run, but module-level imports (like `celeryconfig.py`) happen during test collection, before fixtures are fully set up.
- The environment variable `REDIS_PASSWORD` is not set in the shell environment (as seen in the logged environment variables), and `settings.REDIS_PASSWORD` is likely `None`, so the fallback to `"testpassword"` should kick in—but it’s not happening early enough.

#### Fix
1. **Ensure `setup_test_env` Runs Early**: Since this is a `session`-scoped fixture with `autouse=True`, it should theoretically run at the start of the test session. However, imports happen before this. Move the environment setup to the top of `conftest.py` at module level:
   ```python
   import os
   from dotenv import load_dotenv

   load_dotenv()
   os.environ["REDIS_PASSWORD"] = os.environ.get("REDIS_PASSWORD", "testpassword")
   os.environ["REDIS_URL"] = f"redis://:testpassword@redis:6379/0"
   os.environ["CELERY_BROKER_URL"] = os.environ["REDIS_URL"]
   os.environ["CELERY_RESULT_BACKEND"] = os.environ["REDIS_URL"]
   ```
   Place this right after `load_dotenv()` and before any imports that might trigger `celeryconfig.py`.

2. **Update `setup_test_env`**: Keep it as a fallback, but it’s less critical if the above works:
   ```python
   @pytest.fixture(scope="session", autouse=True)
   def setup_test_env():
       redis_password = settings.REDIS_PASSWORD or "testpassword"
       os.environ["REDIS_PASSWORD"] = redis_password
       os.environ["REDIS_URL"] = f"redis://:{redis_password}@redis:6379/0"
       os.environ["CELERY_BROKER_URL"] = os.environ["REDIS_URL"]
       os.environ["CELERY_RESULT_BACKEND"] = os.environ["REDIS_URL"]
       logger.info("Test environment variables set up")
   ```

3. **Modify `celeryconfig.py`**: Make it more tolerant of missing variables during testing:
   ```python
   def validate_env(var_name: str, var_type: type):
       value = os.environ.get(var_name)
       if value is None and "pytest" in sys.argv[0]:
           logger.warning(f"{var_name} not set during testing; using default")
           return "testpassword" if var_name == "REDIS_PASSWORD" else None
       if value is None:
           raise ValueError(f"{var_name} environment variable is required")
       return var_type(value)
   ```

#### Why This Works
- Setting environment variables at module level ensures they’re available during import time, not just test runtime.
- Adding a test-specific fallback in `validate_env` prevents the error during pytest runs while maintaining strictness in production.

---

### Problem 2: SQLAlchemy URL Parsing Error
The second error occurs when pytest tries to load `conftest.py`:

```
sqlalchemy.exc.ArgumentError: Could not parse SQLAlchemy URL from string ''
```

This happens in:
```python
test_engine: AsyncEngine = create_async_engine(
    settings.TEST_DATABASE_URL,
    echo=True,
    future=True,
)
```

#### Analysis
- `settings.TEST_DATABASE_URL` is an empty string (`''`), which SQLAlchemy can’t parse into a valid database URL (e.g., `postgresql+asyncpg://user:password@host:port/dbname`).
- The logs show `TEST_DATABASE_URL from settings: {settings.TEST_DATABASE_URL}`, but we don’t see the actual value—likely because it’s `None` or unset, and the string representation or default is empty.
- Your `.env` file (loaded via `load_dotenv()`) or `settings.py` isn’t providing a valid `TEST_DATABASE_URL`.
- The environment variables logged don’t include `TEST_DATABASE_URL` or `DATABASE_URL`, suggesting it’s not being picked up.

#### Fix
1. **Check `.env` File**: Ensure your `.env` file (at the project root) contains:
   ```
   TEST_DATABASE_URL=postgresql+asyncpg://testuser:testpass@localhost:5432/test_content_platform
   DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/content_platform
   ```
   Adjust credentials and database names as needed.

2. **Update `settings.py`**: Ensure `TEST_DATABASE_URL` has a fallback in your `src.backend.core.config`:
   ```python
   from pydantic import BaseSettings

   class Settings(BaseSettings):
       DATABASE_URL: str
       TEST_DATABASE_URL: str = "postgresql+asyncpg://testuser:testpass@localhost:5432/test_content_platform"
       REDIS_PASSWORD: str = "testpassword"  # Add this too

       class Config:
           env_file = ".env"
           env_file_encoding = "utf-8"

   settings = Settings()
   ```

3. **Debug in `conftest.py`**: Add a check before creating the engine:
   ```python
   logger.info(f"TEST_DATABASE_URL: {settings.TEST_DATABASE_URL}")
   if not settings.TEST_DATABASE_URL:
       raise ValueError("TEST_DATABASE_URL is not set in settings")
   test_engine: AsyncEngine = create_async_engine(
       settings.TEST_DATABASE_URL,
       echo=True,
       future=True,
   )
   ```

4. **Verify Environment**: Run `pytest` with verbose logging to see the value:
   ```
   pytest src/backend/tests -v --log-cli-level=DEBUG
   ```

#### Why This Works
- Explicitly setting `TEST_DATABASE_URL` in `.env` or as a fallback in `settings.py` ensures it’s never empty.
- Logging and validation catch the issue early, making debugging easier.

---

### Additional Notes
- **Event Loop Warning**: The logs don’t show it, but your `event_loop` fixture might cause issues with async tests. Since Python 3.10+, `asyncio.get_event_loop()` can raise a deprecation warning in some contexts. Your approach with `new_event_loop()` is fine, but ensure it’s not conflicting with SQLAlchemy’s async engine. If you see loop-related errors later, consider removing this fixture and letting pytest-asyncio manage the loop.
- **Alembic Configuration**: The `setup_database` fixture runs migrations, but if the engine fails to initialize, it won’t get that far. Fixing the URL should resolve this downstream.

---

### Next Steps
1. Apply the fixes above.
2. Run `pytest src/backend/tests -v --log-cli-level=DEBUG` again.
3. Share the new logs if there are still issues—I’ll refine the solution further.

This should get your tests running smoothly! Let me know how it goes.