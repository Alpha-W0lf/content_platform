from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict

from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from .api.routers import projects
from .core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup
    yield
    # Shutdown


app = FastAPI(
    title=settings.PROJECT_NAME, version=settings.API_VERSION, lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up Prometheus metrics
Instrumentator().instrument(app).expose(app)

# Include routers
app.include_router(projects.router, prefix="/api/v1", tags=["projects"])


@app.get("/health")
async def health_check() -> Dict[str, str]:
    return {"status": "healthy"}
