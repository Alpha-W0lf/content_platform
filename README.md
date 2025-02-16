# Content Platform

A modern content management and processing platform built with FastAPI and Next.js.

## Features

- Project management with status tracking
- Asset processing and management
- Authentication and authorization
- Modern UI with dark mode support
- API-first design

## Tech Stack

### Backend
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Celery

### Frontend
- Next.js 13+
- TypeScript
- Tailwind CSS
- shadcn/ui

## Development Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd content_platform
```

2. Backend Setup:
```bash
cd src/backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

3. Frontend Setup:
```bash
cd src/frontend
npm install
```

4. Start the development servers:

Backend:
```bash
cd src/backend
uvicorn main:app --reload
```

Frontend:
```bash
cd src/frontend
npm run dev
```

## API Documentation

Once running, visit:
- API docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

Backend tests:
```bash
cd src/backend
pytest
```

Frontend tests:
```bash
cd src/frontend
npm test
```

## License

This is proprietary software. All rights reserved.

This software and its source code are confidential and proprietary. No part of this software may be used, copied, distributed, or modified without explicit written permission from the copyright holder.
