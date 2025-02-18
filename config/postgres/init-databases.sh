#!/bin/bash

set -e
set -u

function create_database() {
    local database=$1
    echo "Creating database '$database'"
    echo "POSTGRES_USER: $POSTGRES_USER"
    echo "database: $database"
    local sql_command="CREATE DATABASE $database WITH OWNER = $POSTGRES_USER ENCODING = 'UTF8' LC_COLLATE = 'en_US.utf8' LC_CTYPE = 'en_US.utf8' TEMPLATE = template0;"
    echo "Debugging: Executing SQL: $sql_command"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "postgres" -c "$sql_command"
    echo "Database '$database' creation completed"
}

if [ -n "$POSTGRES_MULTIPLE_DATABASES" ]; then
    echo "Creating multiple databases: $POSTGRES_MULTIPLE_DATABASES"

    # Log environment variables for debugging
    echo "Debugging: POSTGRES_USER: $POSTGRES_USER"
    echo "Debugging: POSTGRES_DB: $POSTGRES_DB"
    echo "Debugging: POSTGRES_MULTIPLE_DATABASES: $POSTGRES_MULTIPLE_DATABASES"

    for db in $(echo $POSTGRES_MULTIPLE_DATABASES | tr ',' ' '); do
        create_database $db
    done
    echo "Multiple databases created"
fi

if [ -z "$POSTGRES_MULTIPLE_DATABASES" ] && [ -n "$POSTGRES_DB" ]; then
  create_database $POSTGRES_DB
fi
