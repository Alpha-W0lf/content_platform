import pytest
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from src.backend.models.project import Project
from src.backend.models.asset import Asset

@pytest.mark.asyncio
async def test_create_project(db_session: AsyncSession):
    """Test creating a project in the test database"""
    # Create a test project
    project = Project(
        topic="Test Project",
        status="CREATED"
    )
    
    # Add to session and commit
    async with db_session as session:
        session.add(project)
        await session.flush()  # Flush to generate the ID
        await session.commit()
        await session.refresh(project)
        
        # Verify the project was created
        assert isinstance(project.id, UUID)
        assert project.topic == "Test Project"
        assert project.status == "CREATED"
        
        # Query to verify it's in the database
        result = await session.get(Project, project.id)
        assert result is not None
        assert result.id == project.id
        assert result.topic == "Test Project"

@pytest.mark.asyncio
async def test_project_status_transition(db_session: AsyncSession):
    """Test project status transitions"""
    project = Project(topic="Status Test", status="CREATED")
    
    async with db_session as session:
        session.add(project)
        await session.commit()
        await session.refresh(project)
        
        # Test status transition
        project.status = "PROCESSING"
        await session.commit()
        await session.refresh(project)
        assert project.status == "PROCESSING"
        
        project.status = "COMPLETED"
        await session.commit()
        await session.refresh(project)
        assert project.status == "COMPLETED"

@pytest.mark.asyncio
async def test_project_asset_relationship(db_session: AsyncSession):
    """Test project-asset relationship"""
    project = Project(topic="Asset Test", status="CREATED")
    
    async with db_session as session:
        session.add(project)
        await session.flush()
        
        # Create and add assets
        asset1 = Asset(
            project_id=project.id,
            asset_type="script",
            path="/path/to/script.txt",
        )
        asset2 = Asset(
            project_id=project.id,
            asset_type="video",
            path="/path/to/video.mp4",
        )
        
        project.assets.extend([asset1, asset2])
        await session.commit()
        await session.refresh(project)
        
        # Verify relationships
        assert len(project.assets) == 2
        assert any(asset.asset_type == "script" for asset in project.assets)
        assert any(asset.asset_type == "video" for asset in project.assets)

@pytest.mark.asyncio
async def test_project_cascade_delete(db_session: AsyncSession):
    """Test that deleting a project cascades to its assets"""
    project = Project(topic="Cascade Test", status="CREATED")
    
    async with db_session as session:
        session.add(project)
        await session.flush()
        
        asset = Asset(
            project_id=project.id,
            asset_type="script",
            path="/path/to/script.txt",
        )
        project.assets.append(asset)
        await session.commit()
        
        # Delete project
        await session.delete(project)
        await session.commit()
        
        # Verify project and asset are deleted
        result = await session.get(Project, project.id)
        assert result is None
        
        # Verify asset is also deleted
        stmt = select(Asset).where(Asset.project_id == project.id)
        result = await session.execute(stmt)
        assets = result.scalars().all()
        assert len(assets) == 0

@pytest.mark.asyncio
async def test_project_timestamps(db_session: AsyncSession):
    """Test that timestamps are automatically set and updated"""
    project = Project(topic="Timestamp Test", status="CREATED")
    
    async with db_session as session:
        # Test created_at
        session.add(project)
        await session.commit()
        await session.refresh(project)
        assert isinstance(project.created_at, datetime)
        initial_created_at = project.created_at
        
        # Test updated_at changes on update
        project.topic = "Updated Topic"
        await session.commit()
        await session.refresh(project)
        assert project.created_at == initial_created_at  # Should not change
        assert project.updated_at > initial_created_at  # Should be updated