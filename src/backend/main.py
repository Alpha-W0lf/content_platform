from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from src.backend.api.routers import projects
from src.backend.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Instrumentator().instrument(app).expose(app)
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

# Include routers
app.include_router(projects.router, prefix="/api/v1", tags=["projects"])


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
