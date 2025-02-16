import pytest
from httpx import AsyncClient
from uuid import uuid4, UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.backend.schemas.project import ProjectCreate, ProjectStatus
from src.backend.models.project import Project
from sqlalchemy import select

@pytest.mark.asyncio
async def test_create_project(client: AsyncClient, db_session: AsyncSession):
    """Test successful project creation"""
    data = ProjectCreate(topic="Test Topic", notes="Test Notes").model_dump()
    async with client as c:
        response = await c.post("/projects/", json=data)
    
    assert response.status_code == 200
    project = response.json()
    assert project["topic"] == "Test Topic"
    assert project["notes"] == "Test Notes"
    assert project["status"] == "CREATED"
    assert "id" in project
    assert isinstance(UUID(project["id"]), UUID)  # Ensure ID is a valid UUID

    # Check if the project exists in the database
    async with db_session as session:
        retrieved_project = await session.get(Project, UUID(project["id"]))
        assert retrieved_project is not None
        assert retrieved_project.topic == "Test Topic"

@pytest.mark.asyncio
async def test_create_project_missing_topic(client: AsyncClient):
    """Test project creation with missing required field"""
    data = {"notes": "Test Notes"}
    async with client as c:
        response = await c.post("/projects/", json=data)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_project_invalid_topic(client: AsyncClient):
    """Test project creation with invalid topic type (e.g., number instead of string)"""
    data = {"topic": 123, "notes": "Test Notes"}  # Invalid topic type
    async with client as c:
        response = await c.post("/projects/", json=data)
    assert response.status_code == 422  # Expecting a validation error

@pytest.mark.asyncio
async def test_get_project_status(client: AsyncClient, db_session: AsyncSession):
    """Test getting project status"""
    # Create a project first
    project = Project(topic="Test Topic", notes="Test Notes", status="CREATED")
    async with db_session as session:
        session.add(project)
        await session.commit()
        await session.refresh(project)

        # Get its status
        async with client as c:
            status_response = await c.get(f"/projects/{project.id}/status")
        assert status_response.status_code == 200
        status = status_response.json()
        assert status["status"] == "CREATED"

@pytest.mark.asyncio
async def test_get_project_status_not_found(client: AsyncClient):
    """Test getting status of non-existent project"""
    non_existent_id = str(uuid4())
    async with client as c:
        response = await c.get(f"/projects/{non_existent_id}/status")
    assert response.status_code == 404
    assert response.json() == {"detail": "Project not found"}

@pytest.mark.asyncio
async def test_get_project(client: AsyncClient, db_session: AsyncSession):
    """Test getting a project by ID"""
    # Create a project first
    project = Project(topic="Test Topic", notes="Test Notes", status="CREATED")
    async with db_session as session:
        session.add(project)
        await session.commit()
        await session.refresh(project)

        # Get the project
        async with client as c:
            get_response = await c.get(f"/projects/{project.id}")
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
    async with client as c:
        response = await c.get(f"/projects/{non_existent_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Project not found"}

@pytest.mark.asyncio
async def test_get_project_invalid_id(client: AsyncClient):
    """Test getting a project with an invalid ID format"""
    invalid_id = "not-a-uuid"
    async with client as c:
        response = await c.get(f"/projects/{invalid_id}")
    assert response.status_code == 422  # Expecting a validation error

@pytest.mark.asyncio
async def test_list_projects(client: AsyncClient, db_session: AsyncSession):
    """Test getting a list of projects"""
    # Create a few projects
    project1 = Project(topic="Topic 1", notes="Notes 1", status="CREATED")
    project2 = Project(topic="Topic 2", notes="Notes 2", status="PROCESSING")
    async with db_session as session:
        session.add_all([project1, project2])
        await session.commit()

        # Get the list of projects
        async with client as c:
            response = await c.get("/projects/")
        assert response.status_code == 200
        projects = response.json()
        assert isinstance(projects, list)
        assert len(projects) == 2  # Check if both projects are returned

        # Check if the projects have expected data
        topics = {project["topic"] for project in projects}
        assert "Topic 1" in topics
        assert "Topic 2" in topics

@pytest.mark.asyncio
async def test_update_project(client: AsyncClient, db_session: AsyncSession):
    """Test updating a project's fields"""
    # Create initial project
    project = Project(topic="Original Topic", notes="Original Notes", status=ProjectStatus.CREATED)
    async with db_session as session:
        session.add(project)
        await session.commit()
        await session.refresh(project)
        
        # Update the project
        update_data = {
            "topic": "Updated Topic",
            "notes": "Updated Notes"
        }
        async with client as c:
            response = await c.patch(f"/projects/{project.id}", json=update_data)
        
        assert response.status_code == 200
        updated = response.json()
        assert updated["topic"] == "Updated Topic"
        assert updated["notes"] == "Updated Notes"
        assert updated["status"] == ProjectStatus.CREATED  # Status should remain unchanged

@pytest.mark.asyncio
async def test_update_project_status(client: AsyncClient, db_session: AsyncSession):
    """Test updating a project's status"""
    project = Project(topic="Status Update Test", status=ProjectStatus.CREATED)
    async with db_session as session:
        session.add(project)
        await session.commit()
        await session.refresh(project)
        
        # Update to PROCESSING
        update_data = {"status": ProjectStatus.PROCESSING}
        async with client as c:
            response = await c.patch(f"/projects/{project.id}", json=update_data)
        
        assert response.status_code == 200
        updated = response.json()
        assert updated["status"] == ProjectStatus.PROCESSING
        
        # Update to COMPLETED
        update_data = {"status": ProjectStatus.COMPLETED}
        async with client as c:
            response = await c.patch(f"/projects/{project.id}", json=update_data)
        
        assert response.status_code == 200
        updated = response.json()
        assert updated["status"] == ProjectStatus.COMPLETED

@pytest.mark.asyncio
async def test_update_project_not_found(client: AsyncClient):
    """Test updating a non-existent project"""
    non_existent_id = str(uuid4())
    update_data = {"topic": "New Topic"}
    async with client as c:
        response = await c.patch(f"/projects/{non_existent_id}", json=update_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "Project not found"}

@pytest.mark.asyncio
async def test_update_project_invalid_status(client: AsyncClient, db_session: AsyncSession):
    """Test updating a project with an invalid status"""
    project = Project(topic="Invalid Status Test", status=ProjectStatus.CREATED)
    async with db_session as session:
        session.add(project)
        await session.commit()
        await session.refresh(project)
        
        # Try to update with invalid status
        update_data = {"status": "INVALID_STATUS"}
        async with client as c:
            response = await c.patch(f"/projects/{project.id}", json=update_data)
        
        assert response.status_code == 422  # Validation error