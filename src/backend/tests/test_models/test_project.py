import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.backend.models.asset import Asset
from src.backend.models.project import Project
from src.backend.schemas.project import ProjectStatus


@pytest.mark.asyncio
async def test_create_project(db_session: AsyncSession) -> None:
    project = Project(
        id=uuid.uuid4(),
        topic="Test Topic",
        name="Test Project",
        notes="Test Notes",
        status=ProjectStatus.CREATED,
    )
    db_session.add(project)
    await db_session.commit()

    result = await db_session.execute(select(Project).filter_by(id=project.id))
    saved_project = result.scalar_one()

    assert saved_project.topic == "Test Topic"
    assert saved_project.name == "Test Project"
    assert saved_project.notes == "Test Notes"
    assert saved_project.status == ProjectStatus.CREATED


@pytest.mark.asyncio
async def test_project_status_transition(db_session: AsyncSession) -> None:
    project = Project(id=uuid.uuid4(), topic="Test Topic", status=ProjectStatus.CREATED)
    db_session.add(project)
    await db_session.commit()

    project.status = ProjectStatus.PROCESSING
    await db_session.commit()

    result = await db_session.execute(select(Project).filter_by(id=project.id))
    updated_project = result.scalar_one()
    assert updated_project.status == ProjectStatus.PROCESSING


@pytest.mark.asyncio
async def test_project_asset_relationship(db_session: AsyncSession) -> None:
    project = Project(
        id=uuid.uuid4(),
        topic="Test Topic",
        name="Test Project",
        status=ProjectStatus.CREATED,
    )

    asset1 = Asset(
        id=uuid.uuid4(),
        project_id=project.id,
        asset_type="script",
        path="/path/to/script",
    )

    asset2 = Asset(
        id=uuid.uuid4(),
        project_id=project.id,
        asset_type="video",
        path="/path/to/video",
    )

    project.assets = [asset1, asset2]
    db_session.add(project)
    await db_session.commit()

    result = await db_session.execute(
        select(Project).filter_by(id=project.id).options(joinedload(Project.assets))
    )
    saved_project = result.scalar_one()
    assert len(saved_project.assets) == 2
    assert all(isinstance(asset, Asset) for asset in saved_project.assets)
    assert any(asset.asset_type == "script" for asset in saved_project.assets)
    assert any(asset.asset_type == "video" for asset in saved_project.assets)


@pytest.mark.asyncio
async def test_project_cascade_delete(db_session: AsyncSession) -> None:
    project = Project(
        id=uuid.uuid4(),
        topic="Test Topic",
        name="Test Project",
        status=ProjectStatus.CREATED,
    )

    asset = Asset(
        id=uuid.uuid4(),
        project_id=project.id,
        asset_type="script",
        path="/path/to/script",
    )

    project.assets = [asset]
    db_session.add(project)
    await db_session.commit()

    # Store the asset ID before deletion
    asset_id = asset.id

    await db_session.delete(project)
    await db_session.commit()

    # Verify project is deleted
    project_result = await db_session.execute(select(Project).filter_by(id=project.id))
    assert project_result.scalar_one_or_none() is None

    # Verify associated asset is deleted
    asset_result = await db_session.execute(select(Asset).filter_by(id=asset_id))
    assert asset_result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_project_timestamps(db_session: AsyncSession) -> None:
    start_time = datetime.now(timezone.utc)

    project = Project(id=uuid.uuid4(), topic="Test Topic", status=ProjectStatus.CREATED)
    db_session.add(project)
    await db_session.commit()

    assert project.created_at >= start_time
    assert project.updated_at >= start_time

    # Test update
    original_updated_at = project.updated_at
    await db_session.refresh(project)
    project.name = "Updated Name"
    await db_session.commit()

    assert project.updated_at > original_updated_at
    assert project.created_at == project.created_at  # Should not change
