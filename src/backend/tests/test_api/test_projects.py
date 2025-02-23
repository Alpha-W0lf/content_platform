from typing import Any, Dict
from uuid import UUID, uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.models.project import Project
from src.backend.schemas.project import ProjectCreate, ProjectStatus


@pytest.fixture(autouse=True)
async def cleanup_database(db_session: AsyncSession):
    """Clean up the test database before each test."""
    await db_session.execute(delete(Project))
    await db_session.commit()
    yield
    await db_session.execute(delete(Project))
    await db_session.commit()


@pytest.mark.asyncio
async def test_create_project(client: AsyncClient, db_session: AsyncSession): # Use db_session
    """Test successful project creation"""
    data = ProjectCreate(topic="Test Topic", notes="Test Notes").model_dump()
    response = await client.post("/projects/", json=data)  # Use client for API calls
    assert response.status_code == 200
    project = response.json()
    assert project["topic"] == "Test Topic"
    assert project["notes"] == "Test Notes"
    assert project["status"] == "CREATED"
    assert "id" in project
    assert isinstance(UUID(project["id"]), UUID)  # Ensure ID is a valid UUID

    # Check if the project exists in the database, use db_session
    retrieved_project = await db_session.get(Project, project["id"])  # Corrected line
    assert retrieved_project is not None
    assert retrieved_project.topic == "Test Topic"


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
    response = await client.post("/api/v1/projects/", json=data)
    assert response.status_code == 422  # Expecting a validation error


@pytest.mark.asyncio
async def test_get_project_status(client: AsyncClient, db_session: AsyncSession): #add db_session
    """Test getting project status"""
    # Create a project first, directly using db_session
    project = Project(id=uuid4(), topic="Test Topic", notes="Test Notes", status="CREATED")
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project) #get exact created time

    # Get its status using the client (API call)
    status_response = await client.get(f"/projects/{project.id}/status")
    assert status_response.status_code == 200
    status = status_response.json()
    assert status["status"] == "CREATED"


@pytest.mark.asyncio
async def test_get_project_status_not_found(client: AsyncClient, db_session: AsyncSession): #correct the db usage
    """Test getting status of non-existent project"""
    non_existent_id = str(uuid4())
    # Use the client to make the API call
    response = await client.get(f"/projects/{non_existent_id}/status")
    assert response.status_code == 404
    assert response.json() == {"detail": "Project not found"}


@pytest.mark.asyncio
async def test_get_project(client: AsyncClient, db_session: AsyncSession): #added db_session
    """Test getting a project by ID"""
    # Create a project first
    project = Project(id=uuid4(), topic="Test Topic", notes="Test Notes", status="CREATED")
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
    response = await client.get(f"/api/v1/projects/{non_existent_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Project not found"}


@pytest.mark.asyncio
async def test_get_project_invalid_id(client: AsyncClient):
    """Test getting a project with an invalid ID format"""
    invalid_id = "not-a-uuid"
    response = await client.get(f"/projects/{invalid_id}")
    assert response.status_code == 422  # Expecting a validation error
    #assert "Input should be a valid UUID" in response.text #check error message


@pytest.mark.asyncio
async def test_list_projects(client: AsyncClient, db_session: AsyncSession): #added db_session
    """Test getting a list of projects"""
    # Create a few projects
    project1 = Project(id=uuid4(), topic="Topic 1", notes="Notes 1", status="CREATED")
    project2 = Project(id=uuid4(), topic="Topic 2", notes="Notes 2", status="PROCESSING")
    db_session.add_all([project1, project2])
    await db_session.commit()

    # Get the list of projects
    response = await client.get("/projects/")
    assert response.status_code == 200
    projects = response.json()
    assert isinstance(projects, list)
    assert len(projects) == 2  # Check if both projects are returned

    # Check if the projects have expected data (optional, but good practice)
    topics = {project["topic"] for project in projects}
    assert "Topic 1" in topics
    assert "Topic 2" in topics


@pytest.mark.asyncio
async def test_update_project(client: AsyncClient, db_session: AsyncSession):
    """Test updating a project's fields"""
    # Create initial project
    project_id = uuid4()
    project = Project(
        id=project_id,
        topic="Original Topic",
        notes="Original Notes",
        status=ProjectStatus.CREATED,
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    # Update the project
    update_data = {"topic": "Updated Topic", "notes": "Updated Notes"}
    response = await client.patch(f"/api/v1/projects/{project.id}", json=update_data)
    assert response.status_code == 200
    updated = response.json()
    assert updated["topic"] == "Updated Topic"
    assert updated["notes"] == "Updated Notes"
    assert (
        updated["status"] == ProjectStatus.CREATED.value
    )  # Status should remain unchanged


@pytest.mark.asyncio
async def test_update_project_status(client: AsyncClient, db_session: AsyncSession):
    """Test updating a project's status"""
    project_id = uuid4()
    project = Project(
        id=project_id, topic="Status Update Test", status=ProjectStatus.CREATED
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    # Update to PROCESSING
    update_data = {"status": ProjectStatus.PROCESSING.value}
    response = await client.patch(f"/api/v1/projects/{project.id}", json=update_data)
    assert response.status_code == 200
    updated = response.json()
    assert updated["status"] == ProjectStatus.PROCESSING.value

    # Update to COMPLETED
    update_data = {"status": ProjectStatus.COMPLETED.value}
    response = await client.patch(f"/api/v1/projects/{project.id}", json=update_data)
    assert response.status_code == 200
    updated = response.json()
    assert updated["status"] == ProjectStatus.COMPLETED.value


@pytest.mark.asyncio
async def test_update_project_not_found(client: AsyncClient):
    """Test updating a non-existent project"""
    non_existent_id = str(uuid4())
    update_data = {"topic": "New Topic"}
    url = f"/api/v1/projects/{non_existent_id}"
    response = await client.patch(url, json=update_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "Project not found"}


@pytest.mark.asyncio
async def test_update_project_invalid_status(
    client: AsyncClient, db_session: AsyncSession
):
    """Test updating a project with an invalid status"""
    project_id = uuid4()
    project = Project(
        id=project_id, topic="Invalid Status Test", status=ProjectStatus.CREATED
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    # Try to update with invalid status
    update_data = {"status": "INVALID_STATUS"}
    response = await client.patch(f"/api/v1/projects/{project.id}", json=update_data)
    assert response.status_code == 422  # Validation error
