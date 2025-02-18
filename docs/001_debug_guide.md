Okay, I see several issues in your Docker logs, and I'll explain the best approach to debugging and testing in this situation.  You're facing problems that span multiple services, so a structured, layered approach is essential.

**The Problems (from the logs):**

1.  **Redis Configuration Error (Critical):**

    ```
    redis-1          | *** FATAL CONFIG FILE ERROR (Redis 7.4.2) ***
    redis-1          | Reading the configuration file, at line 15
    redis-1          | >>> 'protected-mode "no" "#" "Allow" "connections" "from" "other" "containers"'
    redis-1          | wrong number of arguments
    redis-1          | Starting redis-stack-server, database path /var/lib/redis-stack
    ```

    This is the most immediate and critical issue.  Redis is failing to start because of a problem in its configuration.  It looks like the `protected-mode no` setting is being misinterpreted.  The extra quotes and comment characters (`"#"`, `"Allow"`, `"connections"`, `"from"`, `"other"`, `"containers"`) are being passed as arguments, which is incorrect.  This is likely due to how you've configured the `command` in your `docker-compose.yml` for the `redis` service.

2.  **PostgreSQL Grafana Database Creation Error (Critical):**

    ```
    postgres-1       | 2025-02-18 17:35:19.718 UTC [69] ERROR:  syntax error at or near "user" at character 46
    postgres-1       | 2025-02-18 17:35:19.718 UTC [69] STATEMENT:  CREATE DATABASE grafana
    postgres-1       |              WITH OWNER = user
    ...
    grafana-1        | Error: ✗ pq: database "grafana" does not exist
    ```

    The PostgreSQL initialization script (`init-databases.sh`) is failing to create the `grafana` database. The error message "syntax error at or near 'user'" indicates a problem with the `CREATE DATABASE` command. It's likely due to the way you are using `psql` and variables inside the script, and how they get expanded.  This is preventing Grafana from starting up properly, as it cannot connect to its database.

3. **Celery Connection Error (Critical):**
    ```
    celery_worker-1  | [2025-02-18 17:35:20,945: ERROR/MainProcess] consumer: Cannot connect to redis://:**@redis:6379/0: Error -2 connecting to redis:6379. Name or service not known..
    ```
    The Celery worker is unable to connect to Redis. Although the redis service name should technically work in Docker Compose, this often indicates that Redis isn't running (due to problem #1) or that there's a network issue within the Docker Compose network.

4.  **Potential Grafana Startup Issue (Critical):**

    Even *after* PostgreSQL creates the database, Grafana reports `database "grafana" does not exist`. This *could* be a timing issue (Grafana tries to connect before the database is *fully* ready), but it could also indicate a connection problem between the `grafana` service and the `postgres` service.  The `Error: ✗ pq: database "grafana" does not exist` strongly suggests a connection string or access issue.

**Debugging and Testing Approach (Prioritized):**

You're right that you're currently in a "debugging" phase, working with logs. However, you need to combine this with a more systematic approach:

1.  **Fix Configuration Errors (Immediate):**  Before doing *any* testing, you *must* fix the obvious configuration errors.  These are show-stoppers.

    *   **Redis:**  Modify your `docker-compose.yml` for the `redis` service.  The `command` option needs to be corrected. The correct way to set Redis options is like this (assuming your `.env` file has `REDIS_PASSWORD=password`):

        ```yaml
        redis:
          image: redis/redis-stack:latest
          ports:
            - "6379:6379"
            - "8001:8001"
          volumes:
            - redis_data:/data
          command: >
            redis-stack-server
            --requirepass ${REDIS_PASSWORD:-password}
            --save 60 1
            --loglevel warning
            --protected-mode no  # Corrected: No quotes or comment
          networks:
            - content-platform
          healthcheck:
            test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD:-password}", "ping"]
            interval: 10s
            timeout: 5s
            retries: 5
            start_period: 30s
          restart: unless-stopped
        ```

    *   **PostgreSQL (init-databases.sh):**  The problem is likely in how the `create_database` function is using variables. Here's the corrected `init-databases.sh`:

        ```bash
        #!/bin/bash

        set -e
        set -u

        function create_database() {
            local database=$1
            echo "Creating database '$database'"
            psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "postgres" <<-EOSQL
                CREATE DATABASE $database
                WITH OWNER = $POSTGRES_USER
                ENCODING = 'UTF8'
                LC_COLLATE = 'en_US.utf8'
                LC_CTYPE = 'en_US.utf8'
                TEMPLATE = template0;
        EOSQL
            echo "Database '$database' creation completed"
        }

        if [ -n "$POSTGRES_MULTIPLE_DATABASES" ]; then
            echo "Creating multiple databases: $POSTGRES_MULTIPLE_DATABASES"
            for db in $(echo $POSTGRES_MULTIPLE_DATABASES | tr ',' ' '); do
                create_database $db
            done
            echo "Multiple databases created"
        fi

        ```

        Key Changes:

        *   **`set -u`:**  This is crucial. It makes the script exit immediately if a variable is unset.  This would have caught an error if `$POSTGRES_USER` was not defined.
        *   **`ON_ERROR_STOP=1`:**  This makes `psql` exit immediately if a SQL command fails.  This prevents the script from continuing after an error.
        *   **No extra quotes around `user`**: I removed the extra quotes around "user" in `WITH OWNER`.
        *   **`$database` Variable:** It is critical to use the `$database` variable inside the `create_database` function to expand it correctly.

    * After making *both* of these changes, run:

        ```bash
        docker-compose down -v  # IMPORTANT: Remove volumes to force re-initialization
        docker-compose build --no-cache  # Rebuild images
        docker-compose up
        ```

        The `-v` in `docker-compose down` is *very important* here. It removes the named volumes. Since your database initialization script was failing, the database was likely in a bad state.  Removing the volume forces PostgreSQL to start fresh.
        If you do not remove the volumes, the errors will persist.

2.  **Verify Basic Service Functionality (Manual Checks):**

    After fixing the configuration, before writing automated tests, manually check:

    *   **PostgreSQL:** Can you connect to the `content_platform`, `test_content_platform`, and `grafana` databases using `psql` from *inside* the `api` container (or from your host machine, adjusting the connection parameters)?  You can shell into the running container with `docker-compose exec api sh` (or `psql` directly, if installed on your host).
    *   **Redis:** Can you connect to Redis using `redis-cli` from inside the `api` or `celery_worker` containers (or from your host)?  Try `redis-cli -h redis -a password ping` (assuming your password is "password").
    *   **Grafana:** Can you access the Grafana UI at `http://<your_M2_IP>:3001`?  Can you log in with the default credentials (usually admin/admin)? Can you configure the PostgreSQL data source?
    * **FastAPI:** Can you see swagger at http://localhost:8000/docs

    These manual checks quickly confirm whether the services are running and accessible.

3.  **Unit and Integration Tests (Automated):**

    Now, it's time to write automated tests.  Here's a breakdown of the types of tests and their purpose:

    *   **Unit Tests (Backend - `src/backend/tests/test_api` and `src/backend/tests/test_models`):**
        *   You *already have* good unit tests for your API endpoints and models.  These are *essential*, and you should continue to expand them as you add functionality.
        *   Focus: Testing individual functions and classes in isolation.  They should *not* depend on external services (like a running database).
        *   Use: `pytest` and fixtures (like your `db_session` and `client`) to mock dependencies and control the test environment.
        *  Run your tests frequently to verify the functionality of the API.

    *  **Integration Tests (Backend):** These tests verify that different parts of your *backend* system work together correctly. Examples:

        *  Testing that your API endpoints correctly interact with the database (you already have some of these).
        *  Testing that your Celery tasks correctly update the database.

        These tests *might* use a test database (like your `TEST_DATABASE_URL`), but ideally they still mock external services like Redis if possible (to avoid flakiness).

    * **Integration Tests (Frontend - Backend):** These verify that your *frontend* can communicate with your *backend* correctly. This is where you'll be testing the API calls your Next.js application makes.

       * Create a dedicated testing environment to test with using NEXT_PUBLIC_API_URL.
       * Use tools like React Testing Library or Cypress.
       * Use mock data (similar to the data that the API returns) to isolate your tests.

    *   **End-to-End (E2E) Tests (Frontend + Backend + Infrastructure):**  These are the highest-level tests.  They test the entire system, from the user interface in the browser, through the frontend, backend, database, and any other services.
        *   Use: Tools like Cypress or Playwright.
        *   Run Against:  Ideally, a staging environment that closely mirrors your production environment.
        *   Purpose:  Catch problems that only emerge when all the pieces are integrated.  These are the *most valuable* tests for ensuring overall system correctness, but they are also the most complex to set up and maintain.  You don't need to start with E2E tests, but you should plan for them.

    **Recommendation:**

    1.  **Fix the Redis and PostgreSQL configuration errors.** This is top priority.
    2.  **Verify basic service functionality manually.**
    3.  **Continue expanding your existing backend unit and integration tests.** You're already on the right track with these.
    4.  **Add tests for Celery task execution**.
    5.  **Add integration tests for the frontend.** Test API calls using your `api.ts` file.
    6.  **Plan for E2E tests later**, once you have more core functionality in place.

**Debugging vs. Testing:**

*   **Debugging:**  The process of finding and fixing the *cause* of an existing problem. You're using logs, inspecting variables, and stepping through code.
*   **Testing:** The process of *verifying* that your code works as expected and of *preventing* future problems. You're writing code (tests) that exercises your application code and checks for correct behavior.

You *need* both.  Debugging is reactive; testing is proactive.  Right now, you're forced to debug because of fundamental configuration issues.  Once those are resolved, a strong testing strategy will help you *prevent* regressions and build a more robust application.

**In your current situation, fixing the Redis and PostgreSQL configurations is the absolute first step. Then, continue with your testing, focusing on unit and integration tests, before moving to the frontend.** Don't get bogged down in the Docker logs without addressing the fundamental configuration problems. Once you've fixed those, the logs will become much more useful for diagnosing any remaining issues.
