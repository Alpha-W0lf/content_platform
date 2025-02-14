from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.backend.api.routers import projects
from src.backend.core.config import settings
from src.backend.core.database import engine
from src.backend.models.project import Base
from prometheus_fastapi_instrumentator import Instrumentator
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Prometheus instrumentator first
instrumentator = Instrumentator()

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.API_VERSION
)

# Instrument the app with Prometheus metrics before any other middleware
instrumentator.instrument(app).expose(app)

# Configure CORS - Allow any origin in development, adjust for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(projects.router)

@app.on_event("startup")
async def startup_event():
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")

@app.get("/health")
async def health_check():
    return {"status": "OK"}