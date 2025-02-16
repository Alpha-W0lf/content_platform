import pytest
from httpx import AsyncClient
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from src.backend.schemas.project import ProjectCreate
from src.backend.models.project import Project

@pytest.mark.asyncio
async def test_create_project(client, db_session):
    """Test successful project creation"""
    client = await client
    db_session = await db_session
    data = ProjectCreate(topic="Test Topic", notes="Test Notes").model_dump()
    response = await client.post("/projects/", json=data)
    assert response.status_code == 200
    project = response.json()
    assert project["topic"] == "Test Topic"
    assert project["notes"] == "Test Notes"
    assert project["status"] == "CREATED"
    assert "id" in project

@pytest.mark.asyncio
async def test_create_project_missing_topic(client, db_session):
    """Test project creation with missing required field"""
    client = await client
    db_session = await db_session
    data = {"notes": "Test Notes"}
    response = await client.post("/projects/", json=data)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_get_project_status(client, db_session):
    """Test getting project status"""
    client = await client
    db_session = await db_session
    # Create a project first
    project = Project(topic="Test Topic", notes="Test Notes", status="CREATED")
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    # Get its status
    status_response = await client.get(f"/projects/{project.id}/status")
    assert status_response.status_code == 200
    status = status_response.json()
    assert status["status"] == "CREATED"

@pytest.mark.asyncio
async def test_get_project_status_not_found(client, db_session):
    """Test getting status of non-existent project"""
    client = await client
    db_session = await db_session
    non_existent_id = str(uuid4())
    response = await client.get(f"/projects/{non_existent_id}/status")
    assert response.status_code == 404
    assert response.json() == {"detail": "Project not found"}

@pytest.mark.asyncio
async def test_get_project(client, db_session):
    """Test getting a project by ID"""
    client = await client
    db_session = await db_session
    # Create a project first
    project = Project(topic="Test Topic", notes="Test Notes", status="CREATED")
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    # Get the project
    get_response = await client.get(f"/projects/{project.id}")
    assert get_response.status_code == 200
    project_data = get_response.json()
    assert project_data["id"] == str(project.id)
    assert project_data["topic"] == "Test Topic"
    assert project_data["notes"] == "Test Notes"
    assert project_data["status"] == "CREATED"