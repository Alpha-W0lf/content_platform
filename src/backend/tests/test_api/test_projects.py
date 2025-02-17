from typing import Any, Dict, List
from uuid import UUID, uuid4

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.models.project import Project
from src.backend.schemas.project import ProjectCreate, ProjectStatus


@pytest.mark.asyncio
async def test_create_project(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test successful project creation"""
    data = ProjectCreate(
        topic="Test Topic", notes="Test Notes", name="Test Name"
    ).model_dump()
    response = await client.post("/api/v1/projects/", json=data)

    assert response.status_code == status.HTTP_201_CREATED
    project_dict = response.json()
    assert project_dict["topic"] == "Test Topic"
    assert project_dict["notes"] == "Test Notes"
    assert project_dict["name"] == "Test Name"
    assert project_dict["status"] == ProjectStatus.CREATED.value
    assert "id" in project_dict
    assert isinstance(UUID(project_dict["id"]), UUID)

    # Check if the project exists in the database
    retrieved_project = await db_session.get(Project, UUID(project_dict["id"]))
    assert retrieved_project is not None
    assert retrieved_project.topic == "Test Topic"
    assert retrieved_project.name == "Test Name"


@pytest.mark.asyncio
async def test_create_project_missing_topic(client: AsyncClient) -> None:
    """Test project creation with missing required field"""
    data: Dict[str, Any] = {"notes": "Test Notes"}
    response = await client.post("/api/v1/projects/", json=data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_project_invalid_topic(client: AsyncClient) -> None:
    """Test project creation with invalid topic type (e.g., number instead of string)"""
    data: Dict[str, Any] = {"topic": 123, "notes": "Test Notes"}  # Invalid topic type
    response = await client.post("/projects/", json=data)
    assert response.status_code == 422  # Expecting a validation error


@pytest.mark.asyncio
async def test_get_project_status(client: AsyncClient, db_session: AsyncSession):
    """Test getting project status"""
    # Create a project first
    project = Project(
        id=uuid4(), topic="Test Topic", notes="Test Notes", status=ProjectStatus.CREATED
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    # Get its status
    status_response = await client.get(f"/projects/{project.id}/status")
    assert status_response.status_code == 200
    status = status_response.json()
    assert status["status"] == "CREATED"


@pytest.mark.asyncio
async def test_get_project_status_not_found(client: AsyncClient):
    """Test getting status of non-existent project"""
    non_existent_id = str(uuid4())
    response = await client.get(f"/projects/{non_existent_id}/status")
    assert response.status_code == 404
    assert response.json() == {"detail": "Project not found"}


@pytest.mark.asyncio
async def test_get_project(client: AsyncClient, db_session: AsyncSession):
    """Test getting a project by ID"""
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


@pytest.mark.asyncio
async def test_get_project_not_found(client: AsyncClient):
    """Test getting a non-existent project by ID"""
    non_existent_id = str(uuid4())
    response = await client.get(f"/projects/{non_existent_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Project not found"}


@pytest.mark.asyncio
async def test_get_project_invalid_id(client: AsyncClient):
    """Test getting a project with an invalid ID format"""
    invalid_id = "not-a-uuid"
    response = await client.get(f"/projects/{invalid_id}")
    assert response.status_code == 422  # Expecting a validation error


@pytest.mark.asyncio
async def test_list_projects(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test getting a list of projects"""
    # Create a few projects
    project1 = Project(
        id=uuid4(), topic="Topic 1", notes="Notes 1", status=ProjectStatus.CREATED
    )
    project2 = Project(
        id=uuid4(), topic="Topic 2", notes="Notes 2", status=ProjectStatus.PROCESSING
    )
    db_session.add_all([project1, project2])
    await db_session.commit()

    # Get the list of projects
    response = await client.get("/projects/")
    assert response.status_code == 200
    projects_list: List[Dict[str, Any]] = response.json()
    assert isinstance(projects_list, list)
    assert len(projects_list) == 2

    # Check if the projects have expected data
    topics: set[str] = {str(p["topic"]) for p in projects_list}
    assert "Topic 1" in topics
    assert "Topic 2" in topics


@pytest.mark.asyncio
async def test_update_project(client: AsyncClient, db_session: AsyncSession):
    """Test updating a project's fields"""
    # Create initial project
    project = Project(
        topic="Original Topic", notes="Original Notes", status=ProjectStatus.CREATED
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    # Update the project
    update_data = {"topic": "Updated Topic", "notes": "Updated Notes"}
    response = await client.patch(f"/projects/{project.id}", json=update_data)

    assert response.status_code == 200
    updated = response.json()
    assert updated["topic"] == "Updated Topic"
    assert updated["notes"] == "Updated Notes"
    assert updated["status"] == ProjectStatus.CREATED  # Status should remain unchanged


@pytest.mark.asyncio
async def test_update_project_status(client: AsyncClient, db_session: AsyncSession):
    """Test updating a project's status"""
    project = Project(topic="Status Update Test", status=ProjectStatus.CREATED)
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    # Update to PROCESSING
    update_data = {"status": ProjectStatus.PROCESSING}
    response = await client.patch(f"/projects/{project.id}", json=update_data)

    assert response.status_code == 200
    updated = response.json()
    assert updated["status"] == ProjectStatus.PROCESSING

    # Update to COMPLETED
    update_data = {"status": ProjectStatus.COMPLETED}
    response = await client.patch(f"/projects/{project.id}", json=update_data)

    assert response.status_code == 200
    updated = response.json()
    assert updated["status"] == ProjectStatus.COMPLETED


@pytest.mark.asyncio
async def test_update_project_not_found(client: AsyncClient):
    """Test updating a non-existent project"""
    non_existent_id = str(uuid4())
    update_data = {"topic": "New Topic"}
    response = await client.patch(f"/projects/{non_existent_id}", json=update_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "Project not found"}


@pytest.mark.asyncio
async def test_update_project_invalid_status(
    client: AsyncClient, db_session: AsyncSession
):
    """Test updating a project with an invalid status"""
    project = Project(topic="Invalid Status Test", status=ProjectStatus.CREATED)
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    # Try to update with invalid status
    update_data = {"status": "INVALID_STATUS"}
    response = await client.patch(f"/projects/{project.id}", json=update_data)

    assert response.status_code == 422  # Validation error
