# All tasks completed for this guide.

Okay, I've reviewed your repository and the logs you provided. You're facing a few interconnected issues, but they are all fixable. Here's a breakdown, prioritized by criticality, and a guide to solve them:

**Critical Issues (Must Fix First)**

1.  **PostgreSQL Initialization Failure (Grafana Database):**

    *   **Problem:** The `config/postgres/init-databases.sh` script is failing to create the `grafana` database.  This prevents Grafana from starting correctly, as it cannot connect to its database. The error message in the logs is:
        ```
        postgres-1       | 2025-02-18 17:58:56.305 UTC [65] ERROR:  syntax error at or near "user" at character 55
        postgres-1       | 2025-02-18 17:58:56.305 UTC [65] STATEMENT:  CREATE DATABASE content_platform
        postgres-1       |              WITH OWNER = user
        ```
        The script is trying to run `CREATE DATABASE content_platform WITH OWNER = user`, but `user` is being interpreted as part of the SQL syntax, not as a variable.

    *   **Why it's Critical:** Grafana is your monitoring tool.  Without it, you have limited visibility into the health and performance of your application. You also have a defined set of dashboards and datasources which are also failing to load correctly as a result of this.

    *   **Solution:**
        1.  **Correct `init-databases.sh`:** The issue is that the `user` string literal is not being replaced with the variable that you defined in your `docker-compose.yml` file. The best way to fix this is to be explicit about expanding variables. Here's a corrected version of `config/postgres/init-databases.sh` that works with your current setup:

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

            *   **`set -u`:**  This makes the script exit immediately if a variable is unset. This would catch the error if the `$POSTGRES_USER` variable were accidentally missing.
            *   **`psql` command:** I am using the `$database` and the `$POSTGRES_USER` variables inside of the psql command to ensure that the variables are used correctly.
        2.  **Rebuild and Restart:** After making this change, you *must* rebuild your PostgreSQL container and remove its volume to ensure the initialization script runs correctly:

            ```bash
            docker-compose down -v  # IMPORTANT: Remove volumes (-v)
            docker-compose build --no-cache postgres
            docker-compose up
            ```

            The `-v` flag in `docker-compose down` is *essential* here.  It removes the named volumes attached to your containers.  Since your PostgreSQL initialization script was failing, the database was likely in an incomplete or corrupted state.  Removing the volume forces PostgreSQL to start fresh with a clean database.  If you don't remove the volume, the error will likely persist.  The `--no-cache` flag in `docker-compose build` is also crucial; it forces Docker to rebuild the image from scratch, ignoring any cached layers. This ensures that your changes to `init-databases.sh` are actually used.

2. **Grafana `pg_isready` Command Not Found:**
   * **Problem:** The `grafana-init.sh` script is failing because the `pg_isready` command is not found within the Grafana container's environment. The logs show:
       ```
       grafana-1 | /grafana-init.sh: line 6: pg_isready: command not found
       ```
   *   **Why it's Critical:** The `grafana-init.sh` script is designed to wait for PostgreSQL to be ready before starting Grafana. Without `pg_isready`, the script cannot determine if PostgreSQL is available, potentially leading to Grafana failing to start or connecting to an uninitialized database.
    *  **Solution:**

       1. **Use `wget` for Health Check:** The simplest and most reliable solution is to use `wget` (which is already installed in the Grafana image) to check Grafana's health endpoint. Replace the `pg_isready` check with a check to Grafana's `/api/health` endpoint, which is the standard way to check Grafana's status.  Modify `config/grafana/grafana-init.sh` to be:

          ```bash
          #!/bin/bash
          set -e

          # Wait for PostgreSQL to be ready by checking Grafana's health endpoint.
          echo "Waiting for Grafana to be ready..."
          until wget --spider -q "http://localhost:3000/api/health"; do
            sleep 2
          done

          echo "Grafana is ready, starting..."
          exec /run.sh
          ```

       2. **Rebuild Grafana:** Rebuild the Grafana container to include the updated script:

          ```bash
          docker-compose build --no-cache grafana
          docker-compose up -d
          ```

**Important Notes After Fixing These:**

*   **Volume Removal:** As emphasized above, make sure you use `docker-compose down -v` to remove the PostgreSQL volume when fixing the initialization script.
*   **Testing:** After applying these fixes, thoroughly test:
    *   Can you access the Grafana UI at `<your M2 IP>:3001`?
    *   Can you log in with the default credentials (usually admin/admin)?
    *   Can you configure the PostgreSQL data source in Grafana (using the credentials from your `docker-compose.yml` and the service name `postgres` as the host)?

Once these two issues are resolved, your core infrastructure (PostgreSQL and Grafana) should be stable, and you'll have proper monitoring in place. We can then move on to less critical but still important issues, such as celery worker startup, after you have confirmed that the above are working.
