#!/bin/bash

echo "Running code quality checks..."

# Format code
echo "\n🔍 Running isort..."
isort src/
echo "✅ isort complete"

echo "\n🔍 Running black..."
black src/
echo "✅ black complete"

# Run linting
echo "\n🔍 Running flake8..."
flake8 src/
echo "✅ flake8 complete"

# Run type checking
echo "\n🔍 Running mypy..."
mypy src/
echo "✅ mypy complete"

# Optional: Run pyright (if installed globally)
if command -v pyright &> /dev/null; then
    echo "\n🔍 Running pyright..."
    pyright src/
    echo "✅ pyright complete"
fi

echo "\n✨ All checks completed!"
