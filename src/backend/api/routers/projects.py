import uuid
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core.database import get_db
from src.backend.models.project import Project
from src.backend.schemas.project import (
    ProjectCreate,
    ProjectRead,
    ProjectStatus,
    ProjectUpdate,
)
from src.backend.tasks.broker_test import test_broker_settings
from src.backend.tasks.project_tasks import redis_interaction_test, test_task

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/test-broker")
async def test_redis_broker() -> Dict[str, Any]:
    """
    Test Redis broker settings and authentication.
    Returns detailed diagnostics about the Redis connection.
    """
    result = test_broker_settings.delay()
    return result.get(timeout=10)  # Wait up to 10 seconds for results


@router.get("/test-tasks")
async def run_test_tasks() -> Dict[str, str]:
    """
    Run test tasks for debugging Redis connection.
    """
    redis_test = redis_interaction_test.delay()
    task_test = test_task.delay(2, 2)

    return {
        "redis_interaction_test": redis_test.id,
        "test_task": task_test.id,
        "redis_result": redis_test.get(timeout=10),  # Wait up to 10 seconds
        "task_result": str(task_test.get(timeout=10)),
    }


@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate, db: AsyncSession = Depends(get_db)
) -> ProjectRead:
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


@router.get("/{project_id}/status", response_model=ProjectStatus)
async def get_status(
    project_id: str, db: AsyncSession = Depends(get_db)
) -> ProjectStatus:
    result = await db.execute(select(Project).filter(Project.id == project_id))
    db_project = result.scalar_one_or_none()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project.status


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(
    project_id: str, db: AsyncSession = Depends(get_db)
) -> ProjectRead:
    result = await db.execute(select(Project).filter(Project.id == project_id))
    db_project = result.scalar_one_or_none()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectRead.model_validate(db_project)


@router.get("/", response_model=List[ProjectRead])
async def list_projects(db: AsyncSession = Depends(get_db)) -> List[ProjectRead]:
    result = await db.execute(select(Project))
    projects = result.scalars().all()
    return [ProjectRead.model_validate(p) for p in projects]


@router.patch("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: str, project_update: ProjectUpdate, db: AsyncSession = Depends(get_db)
) -> ProjectRead:
    result = await db.execute(select(Project).filter(Project.id == project_id))
    db_project = result.scalar_one_or_none()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    update_data = project_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_project, field, value)

    await db.commit()
    await db.refresh(db_project)
    return ProjectRead.model_validate(db_project)
