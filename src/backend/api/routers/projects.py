from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core.database import get_db
from src.backend.models.project import Project
from src.backend.schemas.project import ProjectCreate, Project as ProjectSchema, ProjectStatus

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=ProjectSchema)
async def create_project(
    project_create: ProjectCreate, db: AsyncSession = Depends(get_db)
):
    project = Project(**project_create.model_dump())
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


@router.get("/{project_id}/status", response_model=ProjectStatus)
async def get_status(project_id: UUID, db: AsyncSession = Depends(get_db)):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectStatus(status=project.status)

@router.get("/{project_id}", response_model=ProjectSchema)
async def get_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project