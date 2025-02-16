import pytest
from uuid import UUID
from src.backend.models.project import Project

@pytest.mark.asyncio
async def test_create_project(db_session):
    """Test creating a project in the test database"""
    async for db_session in db_session:
        # Create a test project
        project = Project(
            topic="Test Project",
            status="CREATED"
        )
        
        # Add to session and commit
        db_session.add(project)
        await db_session.flush()  # Flush to generate the ID
        await db_session.commit()
        await db_session.refresh(project)
        
        # Verify the project was created
        assert isinstance(project.id, UUID)
        assert project.topic == "Test Project"
        assert project.status == "CREATED"
        
        # Query to verify it's in the database
        result = await db_session.get(Project, project.id)
        assert result is not None
        assert result.id == project.id
        assert result.topic == "Test Project"