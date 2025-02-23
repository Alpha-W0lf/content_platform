#!/bin/bash

# Function to show help message
show_help_message() {
    echo -e "\n💡 Tip: You can automatically fix formatting issues by running:"
    echo "   ./run-checks.sh --fix"
    echo "   Note: Linting and type issues will need to be fixed manually."
}

# Function to run checks locally
run_checks() {
    echo "Running checks in local environment..."
    # Activate virtual environment
    if [ ! -f src/backend/.venv/bin/activate ]; then
        echo "❌ Virtual environment not found at src/backend/.venv. Please set it up first."
        exit 1
    fi
    source src/backend/.venv/bin/activate

    # Initialize error tracking
    HAS_ERRORS=0

    # Define a helper function to run and display results
    run_check() {
        local tool_name="$1"
        local command="$2"
        echo "🔍 Running $tool_name..."
        # Execute the command and capture both stdout and stderr
        OUTPUT=$($command 2>&1)
        RESULT=$?
        echo "$OUTPUT"
        if [ $RESULT -eq 0 ]; then
            echo "✅ $tool_name complete: No errors found"
        else
            echo "❌ $tool_name failed!"
            HAS_ERRORS=1
        fi
        echo "----------------------------------------"
    }

    # Run each check
    run_check "isort" "isort --check-only src/"
    run_check "black" "black --check src/"
    if [ -f .flake8 ]; then
        run_check "flake8" "flake8 src/"
    else
        run_check "flake8" "flake8 src/ --exclude src/backend/.venv"
    fi
    if [ -f mypy.ini ]; then
        run_check "mypy" "mypy --config-file mypy.ini src/"
    else
        run_check "mypy" "mypy src/"
    fi
    if command -v pyright &> /dev/null; then
        run_check "pyright" "pyright src/"
    else
        echo "⚠️ pyright not installed locally, skipping..."
    fi

    # Deactivate virtual environment
    deactivate

    # Final status
    if [ $HAS_ERRORS -eq 0 ]; then
        echo "✨ All checks completed successfully!"
    else
        echo "❌ Some checks failed. See details above."
    fi

    # Show help message
    show_help_message

    return $HAS_ERRORS
}

# Function to fix formatting locally
fix_formatting() {
    echo "Fixing code formatting in local environment..."
    if [ ! -f src/backend/.venv/bin/activate ]; then
        echo "❌ Virtual environment not found at src/backend/.venv. Please set it up first."
        exit 1
    fi
    source src/backend/.venv/bin/activate

    local HAS_ERRORS=0

    echo "🔍 Running isort..."
    isort src/ || HAS_ERRORS=1
    echo "✅ isort complete"

    echo "🔍 Running black..."
    black src/ || HAS_ERRORS=1
    echo "✅ black complete"

    deactivate

    if [ $HAS_ERRORS -eq 0 ]; then
        echo "✨ Formatting fixed successfully!"
    else
        echo "❌ Some formatting operations failed. Please check the output above."
    fi

    return $HAS_ERRORS
}

# Parse command line arguments
if [ "$1" = "--fix" ]; then
    fix_formatting
    exit $?
else
    run_checks
    exit $?
fi