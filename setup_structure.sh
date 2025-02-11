#!/bin/bash

# Create backend directory structure
mkdir -p src/backend/{api/routers,core,models,schemas,modules,prompts,tasks,migrations/versions}
mkdir -p src/backend/tests/{test_api,test_models,test_modules}

# Create frontend directory structure
mkdir -p src/frontend/{app,components,lib,styles,types,public}
mkdir -p src/frontend/app/projects/[projectId]
mkdir -p src/frontend/app/\(auth\)/sign-in/[[...sign-in]]
mkdir -p src/frontend/app/\(auth\)/sign-up/[[...sign-up]]

# Create other directories
mkdir -p .docker data/projects docs .github

# Create backend __init__.py files
touch src/backend/{__init__.py,api/__init__.py,api/routers/__init__.py,core/__init__.py}
touch src/backend/{models/__init__.py,schemas/__init__.py,modules/__init__.py}
touch src/backend/{prompts/__init__.py,tasks/__init__.py,migrations/__init__.py}
touch src/backend/tests/{__init__.py,test_api/__init__.py,test_models/__init__.py,test_modules/__init__.py}

# Create initial backend files
touch src/backend/main.py
touch src/backend/api/{routers/projects.py,dependencies.py}
touch src/backend/core/{config.py,database.py,utils.py}
touch src/backend/models/{project.py,asset.py}
touch src/backend/schemas/{project.py,asset.py}
touch src/backend/{tasks/project_tasks.py,celeryconfig.py}
touch src/backend/migrations/{env.py,script.py.mako}
touch src/backend/tests/conftest.py

# Create frontend files
touch src/frontend/app/{page.tsx,layout.tsx}
touch src/frontend/lib/{api.ts,auth.ts}
touch src/frontend/styles/globals.css
touch src/frontend/types/index.d.ts
touch src/frontend/{.env.local,.eslintrc.json,.prettierrc.json}
touch src/frontend/{next.config.js,package.json,postcss.config.js}
touch src/frontend/{tailwind.config.js,tsconfig.json}
touch src/frontend/app/projects/{page.tsx,[projectId]/page.tsx}
touch src/frontend/app/\(auth\)/sign-in/[[...sign-in]]/page.tsx
touch src/frontend/app/\(auth\)/sign-up/[[...sign-up]]/page.tsx

# Create root level files
touch {.docker/Dockerfile.api,.docker/Dockerfile.celery}
touch {.gitignore,docker-compose.yml,LICENSE,README.md}

echo "Project structure created successfully!"
