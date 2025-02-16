#!/bin/bash
set -e  # Exit on error

echo "Setting up development environment for Content Platform..."

# Make setup scripts executable
echo "Making setup scripts executable..."
chmod +x run-precommit.sh
chmod +x m2_pro_config.sh

# Navigate to backend directory and create virtual environment
cd src/backend
echo "Creating Python virtual environment..."
python3 -m venv .venv

# Activate virtual environment and install dependencies
echo "Activating virtual environment and installing dependencies..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt --upgrade  # Ensure latest versions

# Return to root directory and install pre-commit
cd ../..
echo "Installing pre-commit if not already installed..."
pip install pre-commit --upgrade

echo "Installing pre-commit hooks..."
pre-commit install
pre-commit clean  # Clean any previous pre-commit installations
pre-commit gc  # Clean up any old cached repositories

# Ensure Git hooks are executable
echo "Ensuring Git hooks are executable..."
chmod +x .git/hooks/pre-commit

# Verify installation
echo "Verifying installation..."
pre-commit run --all-files || {
    echo "Error: Pre-commit checks failed. Please check the errors above."
    exit 1
}

echo "Setup complete! Your development environment is ready."
echo "Remember to activate the virtual environment when working:"
echo "cd src/backend && source .venv/bin/activate"
