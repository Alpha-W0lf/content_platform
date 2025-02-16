import pytest
from httpx import AsyncClient
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from src.backend.schemas.project import ProjectCreate

@pytest.mark.asyncio
async def test_create_project(client: AsyncClient, db_session: AsyncSession):
    """Test successful project creation"""
    data = ProjectCreate(topic="Test Topic", notes="Test Notes").model_dump()
    response = await client.post("/projects/", json=data)
    assert response.status_code == 200
    project = response.json()
    assert project["topic"] == "Test Topic"
    assert project["notes"] == "Test Notes"
    assert project["status"] == "CREATED"
    assert "id" in project

@pytest.mark.asyncio
async def test_create_project_missing_topic(client: AsyncClient, db_session: AsyncSession):
    """Test project creation with missing required field"""
    data = {"notes": "Test Notes"}
    response = await client.post("/projects/", json=data)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_get_project_status(client: AsyncClient, db_session: AsyncSession):
    """Test getting project status"""
    # Create a project first
    create_data = ProjectCreate(topic="Test Topic", notes="Test Notes").model_dump()
    create_response = await client.post("/projects/", json=create_data)
    assert create_response.status_code == 200
    project_id = create_response.json()["id"]

    # Get its status
    status_response = await client.get(f"/projects/{project_id}/status")
    assert status_response.status_code == 200
    status = status_response.json()
    assert status["status"] == "CREATED"

@pytest.mark.asyncio
async def test_get_project_status_not_found(client: AsyncClient, db_session: AsyncSession):
    """Test getting status of non-existent project"""
    non_existent_id = str(uuid4())
    response = await client.get(f"/projects/{non_existent_id}/status")
    assert response.status_code == 404
    assert response.json() == {"detail": "Project not found"}

@pytest.mark.asyncio
async def test_get_project(client: AsyncClient, db_session: AsyncSession):
    """Test getting a project by ID"""
    # Create a project first
    create_data = ProjectCreate(topic="Test Topic", notes="Test Notes").model_dump()
    create_response = await client.post("/projects/", json=create_data)
    assert create_response.status_code == 200
    project_id = create_response.json()["id"]

    # Get the project
    get_response = await client.get(f"/projects/{project_id}")
    assert get_response.status_code == 200
    project = get_response.json()
    assert project["id"] == project_id
    assert project["topic"] == "Test Topic"
    assert project["notes"] == "Test Notes"
    assert project["status"] == "CREATED"