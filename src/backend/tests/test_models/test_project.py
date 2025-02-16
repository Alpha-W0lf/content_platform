from datetime import datetime
from uuid import UUID

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.models.asset import Asset
from src.backend.models.project import Project
from src.backend.schemas.project import ProjectStatus


@pytest.mark.asyncio
async def test_create_project(db_session: AsyncSession):
    """Test creating a project in the test database"""
    # Create a test project
    project = Project(topic="Test Project", status=ProjectStatus.CREATED)

    # Add to session and commit
    db_session.add(project)
    await db_session.flush()  # Flush to generate the ID
    await db_session.commit()
    await db_session.refresh(project)

    # Verify the project was created
    assert isinstance(project.id, UUID)
    assert project.topic == "Test Project"
    assert project.status == ProjectStatus.CREATED

    # Query to verify it's in the database
    result = await db_session.get(Project, project.id)
    assert result is not None
    assert result.id == project.id
    assert result.topic == "Test Project"


@pytest.mark.asyncio
async def test_project_status_transition(db_session: AsyncSession):
    """Test project status transitions"""
    project = Project(topic="Status Test", status=ProjectStatus.CREATED)

    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    # Test status transition
    project.status = ProjectStatus.PROCESSING
    await db_session.commit()
    await db_session.refresh(project)
    assert project.status == ProjectStatus.PROCESSING

    project.status = ProjectStatus.COMPLETED
    await db_session.commit()
    await db_session.refresh(project)
    assert project.status == ProjectStatus.COMPLETED


@pytest.mark.asyncio
async def test_project_asset_relationship(db_session: AsyncSession):
    """Test project-asset relationship"""
    project = Project(topic="Asset Test", status=ProjectStatus.CREATED)

    db_session.add(project)
    await db_session.flush()

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
    await db_session.commit()
    await db_session.refresh(project)

    # Verify relationships
    assert len(project.assets) == 2
    assert any(asset.asset_type == "script" for asset in project.assets)
    assert any(asset.asset_type == "video" for asset in project.assets)


@pytest.mark.asyncio
async def test_project_cascade_delete(db_session: AsyncSession):
    """Test that deleting a project cascades to its assets"""
    project = Project(topic="Cascade Test", status=ProjectStatus.CREATED)

    db_session.add(project)
    await db_session.flush()

    asset = Asset(
        project_id=project.id,
        asset_type="script",
        path="/path/to/script.txt",
    )
    project.assets.append(asset)
    await db_session.commit()

    # Delete project
    await db_session.delete(project)
    await db_session.commit()

    # Verify project and asset are deleted
    result = await db_session.get(Project, project.id)
    assert result is None

    # Verify asset is also deleted
    stmt = select(Asset).where(Asset.project_id == project.id)
    result = await db_session.execute(stmt)
    assets = result.scalars().all()
    assert len(assets) == 0


@pytest.mark.asyncio
async def test_project_timestamps(db_session: AsyncSession):
    """Test that timestamps are automatically set and updated"""
    project = Project(topic="Timestamp Test", status=ProjectStatus.CREATED)

    # Test created_at
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    assert isinstance(project.created_at, datetime)
    initial_created_at = project.created_at

    # Test updated_at changes on update
    project.topic = "Updated Topic"
    await db_session.commit()
    await db_session.refresh(project)
    assert project.created_at == initial_created_at  # Should not change
    assert project.updated_at > initial_created_at  # Should be updated
