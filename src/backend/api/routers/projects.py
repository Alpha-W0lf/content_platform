import logging
import uuid
from typing import Any, Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core.database import get_db
from src.backend.models.project import Project
from src.backend.schemas.project import (
    ProjectCreate,
    ProjectRead,
    ProjectStatus,
    ProjectStatusResponse,
    ProjectUpdate,
)
from src.backend.tasks.project_tasks import celery_debug_task as test_task
from src.backend.tasks.project_tasks import redis_interaction_test, test_broker_settings

router = APIRouter(prefix="/projects", tags=["projects"])

logger = logging.getLogger(__name__)


@router.get("/test-broker")
async def test_redis_broker() -> Dict[str, Any]:
    """
    Test Redis broker settings and authentication.
    Returns detailed diagnostics about the Redis connection.
    """
    try:
        result = test_broker_settings.delay()
        return result.get(timeout=10)  # Wait for results
    except OperationalError as e:
        logger.error(f"Database error in test_redis_broker: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )


@router.get("/test-tasks")
async def run_test_tasks() -> Dict[str, str]:
    """
    Run test tasks for debugging Redis connection.
    """
    try:
        redis_test = redis_interaction_test.delay()
        task_test = test_task.delay(2, 2)

        return {
            "redis_interaction_test": redis_test.id,
            "test_task": task_test.id,
            "redis_result": redis_test.get(timeout=10),  # Wait up to 10 seconds
            "task_result": str(task_test.get(timeout=10)),
        }
    except OperationalError as e:
        logger.error(f"Database error in run_test_tasks: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )


@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate, db: AsyncSession = Depends(get_db)
) -> ProjectRead:
    try:
        db_project = Project(
            id=uuid.uuid4(),
            topic=project.topic,
            name=project.name,
            notes=project.notes,
            status=ProjectStatus.CREATED,
        )
        db.add(db_project)
        await db.commit()
        await db.refresh(db_project)
        return ProjectRead.model_validate(db_project)
    except OperationalError as e:
        logger.error(f"Database error in create_project: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )


def validate_uuid(id_str: str) -> UUID:
    """Validate and convert string to UUID."""
    try:
        return UUID(id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid UUID format",
        )


@router.get("/{project_id}/status", response_model=ProjectStatusResponse)
async def get_status(
    project_id: str, db: AsyncSession = Depends(get_db)
) -> ProjectStatusResponse:
    """Get project status by ID."""
    try:
        # Validate UUID format
        project_uuid = validate_uuid(project_id)
        result = await db.execute(select(Project).filter(Project.id == project_uuid))
        db_project = result.scalar_one_or_none()
        if not db_project:
            raise HTTPException(status_code=404, detail="Project not found")
        return ProjectStatusResponse(status=db_project.status)
    except OperationalError as e:
        logger.error(f"Database error in get_status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(
    project_id: str, db: AsyncSession = Depends(get_db)
) -> ProjectRead:
    """Get project by ID."""
    try:
        # Validate UUID format
        project_uuid = validate_uuid(project_id)
        result = await db.execute(select(Project).filter(Project.id == project_uuid))
        db_project = result.scalar_one_or_none()
        if not db_project:
            raise HTTPException(status_code=404, detail="Project not found")
        return ProjectRead.model_validate(db_project)
    except OperationalError as e:
        logger.error(f"Database error in get_project: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )


@router.get("/", response_model=List[ProjectRead])
async def list_projects(db: AsyncSession = Depends(get_db)) -> List[ProjectRead]:
    try:
        result = await db.execute(select(Project))
        projects = result.scalars().all()
        return [ProjectRead.model_validate(p) for p in projects]
    except OperationalError as e:
        logger.error(f"Database error in list_projects: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )


@router.patch("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: str, project_update: ProjectUpdate, db: AsyncSession = Depends(get_db)
) -> ProjectRead:
    """Update project by ID."""
    try:
        # Validate UUID format
        project_uuid = validate_uuid(project_id)
        result = await db.execute(select(Project).filter(Project.id == project_uuid))
        db_project = result.scalar_one_or_none()
        if not db_project:
            raise HTTPException(status_code=404, detail="Project not found")

        update_data = project_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_project, field, value)

        await db.commit()
        await db.refresh(db_project)
        return ProjectRead.model_validate(db_project)
    except OperationalError as e:
        logger.error(f"Database error in update_project: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error",
        )
