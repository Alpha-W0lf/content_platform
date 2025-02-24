import pytest
from httpx import AsyncClient
from uuid import uuid4, UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.backend.schemas.project import ProjectCreate, ProjectStatus
from src.backend.models.project import Project

# No autouse fixture needed here.


@pytest.mark.asyncio
async def test_create_project(client: AsyncClient, db_session: AsyncSession, setup_database):
    """Test successful project creation"""
    data = ProjectCreate(
        topic="Test Topic", notes="Test Notes", name="Test Name"
    ).model_dump()
    response = await client.post("/api/v1/projects/", json=data)
    assert response.status_code == 201  # Use 201 Created
    project_dict = response.json()
    assert project_dict["topic"] == "Test Topic"
    assert project_dict["notes"] == "Test Notes"
    assert project_dict["name"] == "Test Name"
    assert project_dict["status"] == "CREATED"
    assert "id" in project_dict
    assert isinstance(UUID(project_dict["id"]), UUID)

    # Check if the project exists in the database.  Use db_session!
    retrieved_project = await db_session.get(Project, UUID(project_dict["id"]))
    assert retrieved_project is not None
    assert retrieved_project.topic == "Test Topic"
    assert retrieved_project.name == "Test Name"


@pytest.mark.asyncio
async def test_create_project_missing_topic(client: AsyncClient, db_session: AsyncSession, setup_database):
    """Test project creation with missing required field"""
    data = {"notes": "Test Notes"}
    response = await client.post("/api/v1/projects/", json=data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_project_invalid_topic(client: AsyncClient, db_session: AsyncSession, setup_database):
    """Test project creation with invalid topic type"""
    data = {"topic": 123, "notes": "Test Notes"}  # Invalid topic type
    response = await client.post("/api/v1/projects/", json=data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_project_status(client: AsyncClient, db_session: AsyncSession, setup_database):
    """Test getting project status"""
    # Create a project first, directly in the DB
    project = Project(
        id=uuid4(), topic="Test Topic", notes="Test Notes", status="CREATED"
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    # Get its status via the API
    status_response = await client.get(f"/api/v1/projects/{project.id}/status")
    assert status_response.status_code == 200
    status = status_response.json()
    assert status["status"] == "CREATED"

@pytest.mark.asyncio
async def test_get_project_status_not_found(client: AsyncClient, db_session: AsyncSession, setup_database):
    """Test getting status of non-existent project"""
    non_existent_id = str(uuid4())
    response = await client.get(f"/api/v1/projects/{non_existent_id}/status")
    assert response.status_code == 404
    assert response.json() == {"detail": "Project not found"}


@pytest.mark.asyncio
async def test_get_project(client: AsyncClient, db_session: AsyncSession, setup_database):
    """Test getting a project by ID"""
    # Create a project first, directly in the DB
    project = Project(
        id=uuid4(), topic="Test Topic", notes="Test Notes", status="CREATED"
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    # Get the project via the API
    get_response = await client.get(f"/api/v1/projects/{project.id}")
    assert get_response.status_code == 200
    project_data = get_response.json()
    assert project_data["id"] == str(project.id)
    assert project_data["topic"] == "Test Topic"
    assert project_data["notes"] == "Test Notes"
    assert project_data["status"] == "CREATED"


@pytest.mark.asyncio
async def test_get_project_not_found(client: AsyncClient, db_session: AsyncSession, setup_database):
    """Test getting a non-existent project by ID"""
    non_existent_id = str(uuid4())
    response = await client.get(f"/api/v1/projects/{non_existent_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Project not found"}


@pytest.mark.asyncio
async def test_get_project_invalid_id(client: AsyncClient, db_session: AsyncSession, setup_database):
    """Test getting a project with an invalid ID format"""
    invalid_id = "not-a-uuid"
    response = await client.get(f"/api/v1/projects/{invalid_id}")
    assert response.status_code == 422  # Expecting a validation error


@pytest.mark.asyncio
async def test_list_projects(client: AsyncClient, db_session: AsyncSession, setup_database):
    """Test getting a list of projects"""
    # Create a few projects directly in the DB
    project1 = Project(id=uuid4(), topic="Topic 1", notes="Notes 1", status="CREATED")
    project2 = Project(
        id=uuid4(), topic="Topic 2", notes="Notes 2", status="PROCESSING"
    )
    db_session.add_all([project1, project2])
    await db_session.commit()

    # Get the list of projects via the API
    response = await client.get("/api/v1/projects/")
    assert response.status_code == 200
    projects = response.json()
    assert isinstance(projects, list)
    assert len(projects) == 2

    # Check if the projects have expected data (optional, but good practice)
    topics = {project["topic"] for project in projects}
    assert "Topic 1" in topics
    assert "Topic 2" in topics


@pytest.mark.asyncio
async def test_update_project(client: AsyncClient, db_session: AsyncSession, setup_database):
    """Test updating a project's fields."""
    project_id = uuid4()
    # Create project
    project = Project(
        id=project_id, topic="Original topic", notes="Original notes", status="CREATED"
    )
    db_session.add(project)
    await db_session.commit()

    # Update project via API
    updated_data = {"topic": "New topic", "notes": "New notes"}
    response = await client.patch(f"/api/v1/projects/{project_id}", json=updated_data)
    assert response.status_code == 200
    updated_project = response.json()

    # Verify API response
    assert updated_project["topic"] == "New topic"
    assert updated_project["notes"] == "New notes"
    assert updated_project["status"] == "CREATED"  # Status should not change here

    # Verify database state
    retrieved_project = await db_session.get(Project, project_id)
    assert retrieved_project is not None
    assert retrieved_project.topic == "New topic"
    assert retrieved_project.notes == "New notes"
    assert retrieved_project.status == "CREATED"  # type: ignore


@pytest.mark.asyncio
async def test_update_project_status(client: AsyncClient, db_session: AsyncSession, setup_database):
    """Test updating a project's status."""
    project_id = uuid4()
    # Create project
    project = Project(id=project_id, topic="Status Update Test", status="CREATED")
    db_session.add(project)
    await db_session.commit()

    # Update to PROCESSING via API
    response = await client.patch(
        f"/api/v1/projects/{project_id}", json={"status": "PROCESSING"}
    )
    assert response.status_code == 200

    # Verify via DB and API
    retrieved_project = await db_session.get(Project, project_id)
    assert retrieved_project is not None
    assert retrieved_project.status == "PROCESSING"  # type: ignore
    response = await client.get(f"/api/v1/projects/{project_id}")
    assert response.json()["status"] == "PROCESSING"

    # Update to COMPLETED via API
    response = await client.patch(
        f"/api/v1/projects/{project_id}", json={"status": "COMPLETED"}
    )
    assert response.status_code == 200
    updated = response.json()
    assert updated["status"] == "COMPLETED"


@pytest.mark.asyncio
async def test_update_project_not_found(client: AsyncClient, db_session: AsyncSession, setup_database):
    """Test updating a non-existent project."""
    non_existent_id = str(uuid4())
    update_data = {"topic": "New Topic"}
    response = await client.patch(
        f"/api/v1/projects/{non_existent_id}", json=update_data
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Project not found"}


@pytest.mark.asyncio
async def test_update_project_invalid_status(client: AsyncClient, db_session: AsyncSession, setup_database):
    """Test updating a project with an invalid status."""
    project_id = uuid4()

    project = Project(
        id=project_id, topic="Invalid Status Test", status=ProjectStatus.CREATED
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    # Try to update to invalid status
    update_data = {"status": "INVALID_STATUS"}
    response = await client.patch(f"/api/v1/projects/{project.id}", json=update_data)
    assert response.status_code == 422
