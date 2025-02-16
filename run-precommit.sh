#!/bin/bash
# Activate virtualenv and run pre-commit
source src/backend/.venv/bin/activate
pre-commit "$@"
