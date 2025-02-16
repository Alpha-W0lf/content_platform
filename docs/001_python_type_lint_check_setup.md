Below is a step-by-step guide to set up a robust Python workflow that includes type checking, linting, formatting, and pre-commit hooks. You can use **mypy** (a static type checker) alongside **Pylance** (which uses Pyright for real‑time type checking in VS Code) without conflict—they serve complementary roles. Pylance gives you immediate feedback in the editor, while mypy can be run in your CI pipeline or pre-commit hooks for an extra layer of verification.

---

## 1. Set Up Your Environment

1. **Create a Virtual Environment (recommended):**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

2. **Upgrade pip:**

   ```bash
   pip install --upgrade pip
   ```

---

## 2. Install the Necessary Packages

Install the tools we’ll be using:

```bash
pip install mypy flake8 black isort pre-commit
```

You may also install additional plugins for flake8 if needed (e.g., `flake8-import-order`):

```bash
pip install flake8-import-order
```

---

## 3. Configure Each Tool

### **mypy (Type Checking)**
Create a `mypy.ini` (or add a `[mypy]` section to your `pyproject.toml`):

```ini
[mypy]
python_version = 3.10
ignore_missing_imports = True
strict = True
```

*This configuration enforces strict type checking and ignores errors from missing type hints in third-party packages.*

---

### **flake8 (Linting)**
Create a `.flake8` file in your repo:

```ini
[flake8]
max-line-length = 88
extend-ignore = E203, W503
```

*These settings are compatible with Black’s formatting style.*

---

### **Black (Code Formatting) & isort (Import Sorting)**
You can add configuration to your `pyproject.toml` to centralize configuration:

```toml
[tool.black]
line-length = 88

[tool.isort]
profile = "black"
```

*This tells isort to use Black’s style, ensuring they work seamlessly together.*

---

### **pre-commit (Automation)**
Create a `.pre-commit-config.yaml` file:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0  # Use the latest stable version or your preferred version
    hooks:
      - id: black

  - repo: https://github.com/PyCQA/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: local
    hooks:
      - id: mypy
        name: mypy
        entry: mypy .
        language: system
        types: [python]
```

Install the pre-commit hooks:

```bash
pre-commit install
```

*Now, every time you commit changes, these hooks will run automatically, helping to enforce your code quality rules before code is committed.*

---

## 4. VS Code Integration

- **Python Extension & Pylance:**
  Install the official Python extension and Pylance from the VS Code marketplace. Pylance will provide on-the-fly type checking using Pyright.

- **Configure VS Code Settings:**
  In your `settings.json` (via Preferences > Settings > Open Settings (JSON)), add:

  ```json
  {
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.linting.mypyEnabled": true,
    "python.analysis.typeCheckingMode": "strict"
  }
  ```

*This configuration ensures VS Code uses your chosen linters, formatter, and type checker, providing immediate feedback as you code.*

---

## 5. Running the Tools

- **Run mypy manually:**
  ```bash
  mypy .
  ```
- **Run flake8 manually:**
  ```bash
  flake8 .
  ```
- **Format code with Black:**
  ```bash
  black .
  ```
- **Sort imports with isort:**
  ```bash
  isort .
  ```

---

## Using mypy and Pylance Together

They complement each other:
- **Pylance** gives you real‑time, in-editor type checking and IntelliSense powered by Pyright.
- **mypy** can be run as part of your CI pipeline or pre-commit hooks to enforce stricter type checking.

They may occasionally report slightly different issues due to differences in type inference, but they do not conflict.

---

By following these steps, you’ll have a well-integrated workflow that automatically checks for type errors, enforces coding style, and sorts imports, improving overall code quality and consistency.

Would you like any additional details or help with specific configuration options?
