# Setting up the development environment

## Step 1: Python Environment Setup

```bash
cd src/backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## Step 2: Pre-commit Setup

From the root directory:
```bash
pre-commit install
```

## Step 3: Run Configuration Script

```bash
./m2_pro_config.sh
