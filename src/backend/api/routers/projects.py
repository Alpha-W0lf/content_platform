from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core.database import get_db
from src.backend.models.project import Project
from src.backend.schemas.project import Project as ProjectSchema
from src.backend.schemas.project import (
    ProjectCreate,
    ProjectStatusResponse,
    ProjectUpdate,
)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=ProjectSchema)
async def create_project(
    project_create: ProjectCreate, db: AsyncSession = Depends(get_db)
):
    project = Project(**project_create.model_dump())
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project  # Return the Project object, FastAPI will use the response_model


@router.get("/{project_id}/status", response_model=ProjectStatusResponse)
async def get_status(project_id: UUID, db: AsyncSession = Depends(get_db)):
    project = await db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectStatusResponse(
        status=project.status
    )  # Return a ProjectStatusResponse object


@router.get("/{project_id}", response_model=ProjectSchema)
async def get_project(project_id: UUID, db: AsyncSession = Depends(get_db)):
    project = await db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project  # Return the Project object


@router.get("/", response_model=List[ProjectSchema])
async def list_projects(db: AsyncSession = Depends(get_db)):
    query = select(Project)
    result = await db.execute(query)
    projects = result.scalars().all()
    return projects


@router.patch("/{project_id}", response_model=ProjectSchema)
async def update_project(
    project_id: UUID, project_update: ProjectUpdate, db: AsyncSession = Depends(get_db)
):
    project = await db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    update_data = project_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    await db.commit()
    await db.refresh(project)
    return project
