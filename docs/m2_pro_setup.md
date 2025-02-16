step 1:
cd src/backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

step 2:
# From the root directory
pre-commit install

run this script:
m2_pro_config.sh
