# Task Tracking

- [ ] **Backend (Local - M2 Max)**
  - [x] PostgreSQL Setup (Local - M2 Max)
  - [x] Python Environment Setup (Local - M2 Max)
  - [x] Database Migrations (Local - M2 Max)
  - [x] Backend Code (Local - M2 Max)
  - [ ] Run Backend Tests (Local - M2 Max)
  - [ ] Run Backend Server (Local - M2 Max)
- [ ] **Frontend (Local - M2 Max)**
  - [ ] Frontend Setup (Local - M2 Max)
  - [ ] Frontend Code (Local - M2 Max)
  - [ ] Run Frontend Server (Local - M2 Max)
  - [ ] Access Application (From M2 Pro)
- [ ] **Testing**
  - [ ] Backend Tests
  - [ ] Frontend Tests
  - [ ] Manual Testing
- [ ] **Version Control**
  - [ ] Commit Frequently

**I. Backend (Local - M2 Max)**

1.  **PostgreSQL Setup (Local - M2 Max):**

    - **Install PostgreSQL 15:**
      ```bash
      brew install postgresql@15
      ```
    - **Start PostgreSQL:**
      ```bash
      brew services start postgresql@15
      ```
    - **Create Databases:**
      ```bash
      createdb -U user -w content_platform_dev
      createdb -U user -w test_content_platform
      ```
      (Ensure your `.env` file in `src/backend` points to `content_platform_dev`, and `TEST_DATABASE_URL` points to `test_content_platform`, both with user `user` and password `password`)

2.  **Python Environment Setup (Local - M2 Max):** - venv setup should already be done. just verify when you get to this step.

    - **Create/Activate Virtual Environment:** (Inside `src/backend`)
      ```bash
      python3 -m venv .venv
      source .venv/bin/activate  # or .venv\Scripts\activate on Windows
      ```
    - **Install Dependencies:** (Inside `src/backend`)
      ```bash
      pip install -r requirements.txt
      ```
    - **`requirements.txt` (Ensure these exact versions):**

      ```
      fastapi==0.104.1
      uvicorn[standard]==0.24.0
      sqlalchemy==2.0.23
      asyncpg==0.29.0
      alembic==1.13.1
      pydantic==2.5.2
      pydantic-settings==2.1.0
      python-dotenv==1.0.0
      pytest==7.4.3
      pytest-asyncio==0.23.2
      httpx==0.25.2
      python-multipart==0.0.6
      python-slugify==8.0.1
      psycopg2-binary==2.9.9 #DB connection errors if not installed

      # Development dependencies
      mypy==1.8.0
      flake8==7.0.0
      flake8-import-order==0.18.2
      pylint==3.1.0
      black==24.2.0
      isort==5.13.2
      autoflake==2.2.1
      types-redis==4.6.0.20240106
      pyright==1.1.394
      ```

3.  **Database Migrations (Local - M2 Max):**

    - **Run Migrations:** (Inside `src/backend`)
      ```bash
      alembic upgrade head
      ```
      (This creates the `projects` table based on your `Project` model.)

4.  **Backend Code (Local - M2 Max):**

    - **Ensure all backend files are in place** and match the code provided in the previous response. This includes:
      - ✅ `src/backend/main.py`
      - ✅ `src/backend/api/projects.py`
      - ✅ `src/backend/core/config.py`
      - ✅ `src/backend/core/database.py`
      - ✅ `src/backend/models/project.py`
      - ✅ `src/backend/models/base.py`
      - ✅ `src/backend/models/__init__.py`
      - ✅ `src/backend/schemas/project.py`
      - ✅ `src/backend/schemas/__init__.py`
      - ✅ `src/backend/migrations/...` (and all subdirectories)
      - ✅ `src/backend/modules/__init__.py`
      - ✅ `src/backend/tests/conftest.py`
      - ✅ `src/backend/tests/test_api/test_projects.py`
      - ✅ `src/backend/tests/test_models/test_project.py`
      - ✅ `src/backend/tasks/__init__.py`

5.  **Run Backend Tests (Local - M2 Max):**

    - **Execute Tests:** (Inside `src/backend`)
      ```bash
      pytest src/backend/tests
      ```
    - **All tests should pass.** Fix any failing tests before proceeding.

6.  **Run Backend Server (Local - M2 Max):**

    - **Start FastAPI:** (Inside `src/backend`)
      ```bash
      uvicorn src.backend.main:app --reload --host 0.0.0.0 --port 8000
      ```
    - **Verify:** Access `http://localhost:8000/docs` in a browser on your M2 Max (or via port forwarding from your M2 Pro). You should see the FastAPI interactive API documentation.

**II. Frontend (Local - M2 Max)**

1.  **Frontend Setup (Local - M2 Max):**

    - **Navigate:** `cd src/frontend`
    - **Install Dependencies:**
      ```bash
      npm install
      ```
    - **`src/frontend/package.json` (Ensure these exact versions):**

      ```json
      {
        "name": "content-platform",
        "version": "0.1.0",
        "private": true,
        "license": "UNLICENSED",
        "engines": {
          "node": ">=18.17.0",
          "npm": ">=9.0.0"
        },
        "scripts": {
          "dev": "next dev",
          "start": "next start",
          "test": "jest",
          "test:e2e": "cypress run",
          "format": "prettier --write .",
          "build": "next build",
          "lint": "next lint"
        },
        "dependencies": {
          "@clerk/nextjs": "^6.11.3",
          "@radix-ui/react-accordion": "^1.1.2",
          "@radix-ui/react-alert-dialog": "^1.0.5",
          "@radix-ui/react-aspect-ratio": "^1.0.3",
          "@radix-ui/react-avatar": "^1.0.4",
          "@radix-ui/react-checkbox": "^1.0.4",
          "@radix-ui/react-collapsible": "^1.0.3",
          "@radix-ui/react-context-menu": "^2.1.5",
          "@radix-ui/react-dialog": "^1.0.5",
          "@radix-ui/react-dropdown-menu": "^2.0.6",
          "@radix-ui/react-hover-card": "^1.0.7",
          "@radix-ui/react-label": "^2.0.2",
          "@radix-ui/react-menubar": "^1.0.4",
          "@radix-ui/react-navigation-menu": "^1.1.4",
          "@radix-ui/react-popover": "^1.0.7",
          "@radix-ui/react-progress": "^1.0.3",
          "@radix-ui/react-radio-group": "^1.1.3",
          "@radix-ui/react-scroll-area": "^1.0.5",
          "@radix-ui/react-select": "^2.0.0",
          "@radix-ui/react-separator": "^1.0.3",
          "@radix-ui/react-slider": "^1.1.2",
          "@radix-ui/react-slot": "^1.0.2",
          "@radix-ui/react-switch": "^1.0.3",
          "@radix-ui/react-tabs": "^1.0.4",
          "@radix-ui/react-toast": "^1.1.5",
          "@radix-ui/react-toggle": "^1.0.3",
          "@radix-ui/react-toggle-group": "^1.0.4",
          "@radix-ui/react-tooltip": "^1.0.7",
          "@tanstack/react-query": "^5.28.1",
          "@tanstack/react-query-devtools": "^5.28.1",
          "axios": "^1.6.7",
          "class-variance-authority": "^0.7.0",
          "clsx": "^2.1.0",
          "cmdk": "^0.2.1",
          "date-fns": "^2.30.0",
          "lucide-react": "^0.375.0",
          "next": "14.2.24",
          "next-themes": "^0.2.1",
          "react": "18.2.0",
          "react-day-picker": "^8.10.0",
          "react-dom": "18.2.0",
          "tailwind-merge": "^2.2.1",
          "tailwindcss-animate": "^1.0.7"
        },
        "devDependencies": {
          "@types/node": "^20",
          "@types/react": "^18",
          "@types/react-dom": "^18",
          "autoprefixer": "^10.4.20",
          "eslint": "^8",
          "eslint-config-next": "14.2.1",
          "postcss": "^8.4.32",
          "prettier-plugin-tailwindcss": "^0.5.13",
          "tailwindcss": "^3.4.0",
          "typescript": "^5.3.3",
          "jest": "^29.7.0",
          "cypress": "^13.6.6"
        },
        "overrides": {
          "rimraf": "^5.0.0"
        }
      }
      ```

    - **Install shadcn/ui Components:**
      - Run `npx shadcn-ui@latest init` and follow the prompts. This will configure `components.json` and set up the necessary utilities. **Choose the `dark` theme and `slate` as the base color.**
      - Install the required components (you've likely already done this):
        ```bash
        npx shadcn-ui@latest add button input label card
        ```

2.  **Frontend Code (Local - M2 Max):**

    - **Ensure all frontend files are in place** and match the code provided in the previous response, including:

      - `src/frontend/app/page.tsx`
      - `src/frontend/app/projects/page.tsx`
      - `src/frontend/app/projects/[projectId]/page.tsx`
      - `src/frontend/app/layout.tsx`
      - `src/frontend/app/globals.css` (Ensure Tailwind and shadcn/ui are configured)
      - `src/frontend/components/...` (All your shadcn/ui components)
      - `src/frontend/lib/api.ts`
      - `src/frontend/components/project-details.tsx`
      - `src/frontend/components/theme-provider.tsx`
      - `src/frontend/components/theme-toggle.tsx`
      - Make sure that the necessary files are added to the `src/frontend/app/(auth)/sign-in/[[...sign-in]]` and `src/frontend/app/(auth)/sign-up/[[...sign-up]]` folders.
      - **Key Change: `api.ts`:** Update `src/frontend/lib/api.ts` to use `NEXT_PUBLIC_API_URL`:

        ```typescript
        // src/frontend/lib/api.ts
        import axios from "axios";
        import type {
          Project as ProjectSchema,
          ProjectCreate,
          ProjectStatus,
        } from "../types";

        const api = axios.create({
          baseURL: process.env.NEXT_PUBLIC_API_URL, // Use the environment variable
        });

        export const projectsApi = {
          create: async (data: ProjectCreate): Promise<ProjectSchema> => {
            const response = await api.post("/api/v1/projects/", data);
            return response.data;
          },
          listProjects: async (): Promise<ProjectSchema[]> => {
            const response = await api.get("/api/v1/projects/");
            return response.data;
          },
          getProject: async (projectId: string): Promise<ProjectSchema> => {
            const response = await api.get(`/api/v1/projects/${projectId}`);
            return response.data;
          },
          updateProject: async (
            projectId: string,
            data: { status: ProjectStatus }
          ): Promise<ProjectSchema> => {
            const response = await api.patch(
              `/api/v1/projects/${projectId}`,
              data
            );
            return response.data;
          },
        };

        export type { ProjectSchema, ProjectCreate, ProjectStatus };
        ```

3.  **Run Frontend Server (Local - M2 Max):**

    - **Start Next.js:** (Inside `src/frontend`)
      ```bash
      npm run dev
      ```

4.  **Access Application (From M2 Pro):**

- Open your browser on the **M2 Pro** and go to `http://<M2_MAX_IP>:3000`, replacing `<M2_MAX_IP>` with the actual IP address or hostname of your M2 Max. You should also be able to access it via `http://localhost:3000` since you are port forwarding.

**III. Testing**

- **Backend Tests:** Run frequently using `pytest src/backend/tests` (from within `src/backend`).
- **Frontend Tests:** Not included in v0.0, but add them as you build out the frontend.
- **Manual Testing:** Thoroughly test the application in your browser after each significant change.

**IV. Version Control**

- **Commit Frequently:** Commit your code to Git regularly, with clear and descriptive commit messages.
