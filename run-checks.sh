#!/bin/bash

# Function to show help message
show_help_message() {
    echo -e "\n💡 Tip: You can automatically fix formatting issues by running:"
    echo "   ./run-checks.sh --fix"
    echo "   Note: Linting and type issues will need to be fixed manually."
}

# Function to run checks in Docker
run_in_docker() {
    echo "Running checks in Docker environment..."
    
    # Create a temporary directory for Docker operations
    TEMP_DIR=$(mktemp -d)
    
    # Copy source files to temp directory
    echo "📁 Copying files for processing..."
    cp -r src/ "$TEMP_DIR/"
    
    # Use the API container since it has our Python environment
    docker compose exec -T api sh -c "
        cd /app && \
        echo '🔍 Running isort...' && \
        isort --check-only src/ && \
        echo '✅ isort complete' && \
        echo '🔍 Running black...' && \
        black --check src/ && \
        echo '✅ black complete' && \
        echo '🔍 Running flake8...' && \
        flake8 src/ && \
        echo '✅ flake8 complete' && \
        echo '🔍 Running mypy...' && \
        mypy --config-file mypy.ini src/ && \
        echo '✅ mypy complete' && \
        if command -v pyright &> /dev/null; then
            echo '🔍 Running pyright...' && \
            pyright src/ && \
            echo '✅ pyright complete'
        fi && \
        echo '✨ All checks completed!'
    "
    
    # Store the exit code
    EXIT_CODE=$?
    
    # Clean up
    rm -rf "$TEMP_DIR"

    # Show help message regardless of result
    show_help_message
    
    # Return the exit code from the Docker command
    return $EXIT_CODE
}

# Function to run checks and fix locally
run_locally() {
    echo "Running checks in local environment..."
    # Activate virtual environment
    source src/backend/.venv/bin/activate

    echo "Running code quality checks..."

    # Initialize error tracking
    local HAS_ERRORS=0

    # Format code
    echo "🔍 Running isort..."
    isort --check-only src/ || HAS_ERRORS=1
    echo "✅ isort complete"

    echo "🔍 Running black..."
    black --check src/ || HAS_ERRORS=1
    echo "✅ black complete"

    # Run linting
    echo "🔍 Running flake8..."
    flake8 src/ || HAS_ERRORS=1
    echo "✅ flake8 complete"

    # Run type checking
    echo "🔍 Running mypy..."
    mypy --config-file mypy.ini src/ || HAS_ERRORS=1
    echo "✅ mypy complete"

    # Optional: Run pyright (if installed globally)
    if command -v pyright &> /dev/null; then
        echo "🔍 Running pyright..."
        pyright src/ || HAS_ERRORS=1
        echo "✅ pyright complete"
    fi

    # Deactivate virtual environment
    deactivate

    if [ $HAS_ERRORS -eq 0 ]; then
        echo "✨ All checks completed successfully!"
    else
        echo -e "\n❌ Some checks failed. Please fix the issues above."
    fi

    # Show help message regardless of result
    show_help_message

    return $HAS_ERRORS
}

# Function to fix formatting
fix_formatting() {
    echo "Fixing code formatting..."
    local HAS_ERRORS=0

    if docker compose ps | grep -q "content_platform-api.*Up"; then
        echo "🔍 Running formatters in Docker environment..."
        docker compose exec -T api sh -c "
            cd /app && \
            echo '🔍 Running isort...' && \
            isort src/ && \
            echo '✅ isort complete' && \
            echo '🔍 Running black...' && \
            black src/ && \
            echo '✅ black complete'
        " || HAS_ERRORS=1
    else
        echo "🔍 Running formatters in local environment..."
        source src/backend/.venv/bin/activate
        echo "🔍 Running isort..."
        isort src/ || HAS_ERRORS=1
        echo "✅ isort complete"
        echo "🔍 Running black..."
        black src/ || HAS_ERRORS=1
        echo "✅ black complete"
        deactivate
    fi

    if [ $HAS_ERRORS -eq 0 ]; then
        echo "✨ Formatting fixed successfully!"
        return 0
    else
        echo "❌ Some formatting operations failed. Please check the output above."
        return 1
    fi
}

# Parse command line arguments
if [ "$1" = "--fix" ]; then
    fix_formatting
    exit $?
fi

# Check if Docker is running and containers are up
if docker compose ps | grep -q "content_platform-api.*Up"; then
    run_in_docker
    exit $?
else
    echo "Docker not running or API container not found, falling back to local environment..."
    run_locally
    exit $?
fi
