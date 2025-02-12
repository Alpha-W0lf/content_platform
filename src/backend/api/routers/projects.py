from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from core.database import get_db
from models.project import Project
from schemas.project import ProjectCreate, ProjectStatus, Project as ProjectSchema
from uuid import UUID
import logging

router = APIRouter(
    prefix="/projects",
    tags=["projects"]
)

logger = logging.getLogger(__name__)

@router.post("/", response_model=ProjectSchema)
async def create_project(
    project: ProjectCreate,
    db: AsyncSession = Depends(get_db)
):
    # Create project with just the topic, name will be set later
    db_project = Project(
        topic=project.topic,
        notes=project.notes,
        status="CREATED"
    )
    db.add(db_project)
    await db.commit()
    await db.refresh(db_project)
    return db_project

@router.get("/{project_id}/status", response_model=ProjectStatus)
async def get_project_status(
    project_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectStatus(status=project.status)

@router.get("/", response_model=List[ProjectSchema])
async def list_projects(
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Project))
    projects = result.scalars().all()
    return projects