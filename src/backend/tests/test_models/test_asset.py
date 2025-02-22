import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.models.asset import Asset
from src.backend.models.project import Project
from src.backend.schemas.project import ProjectStatus


@pytest.mark.asyncio
async def test_create_asset(db_session: AsyncSession) -> None:
    """Test creating an asset with valid data."""
    start_time = datetime.now(timezone.utc)

    project = Project(id=uuid.uuid4(), topic="Test Topic", status=ProjectStatus.CREATED)
    db_session.add(project)
    await db_session.commit()

    asset = Asset(
        id=uuid.uuid4(),
        project_id=project.id,
        asset_type="script",
        path="/path/to/asset",
    )
    db_session.add(asset)
    await db_session.commit()

    result = await db_session.execute(select(Asset).filter_by(id=asset.id))
    saved_asset = result.scalar_one()
    assert saved_asset.project_id == project.id
    assert saved_asset.asset_type == "script"
    assert saved_asset.path == "/path/to/asset"
    assert saved_asset.created_at >= start_time
    assert saved_asset.updated_at >= start_time


@pytest.mark.asyncio
async def test_asset_updates(db_session: AsyncSession) -> None:
    """Test updating asset fields."""
    project = Project(id=uuid.uuid4(), topic="Test Topic", status=ProjectStatus.CREATED)
    db_session.add(project)
    await db_session.commit()

    asset = Asset(
        id=uuid.uuid4(),
        project_id=project.id,
        asset_type="script",
        path="/path/to/asset",
    )
    db_session.add(asset)
    await db_session.commit()

    asset.path = "/updated/path"
    asset.asset_type = "video"
    await db_session.commit()

    result = await db_session.execute(select(Asset).filter_by(id=asset.id))
    updated_asset = result.scalar_one()
    assert updated_asset.path == "/updated/path"
    assert updated_asset.asset_type == "video"


@pytest.mark.asyncio
async def test_asset_timestamp_updates(db_session: AsyncSession) -> None:
    """Test that timestamps are properly set and updated."""
    start_time = datetime.now(timezone.utc)

    project = Project(id=uuid.uuid4(), topic="Test Topic", status=ProjectStatus.CREATED)
    db_session.add(project)
    await db_session.commit()

    asset = Asset(
        id=uuid.uuid4(),
        project_id=project.id,
        asset_type="script",
        path="/path/to/asset",
    )
    db_session.add(asset)
    await db_session.commit()

    assert asset.created_at >= start_time
    assert asset.updated_at >= start_time

    # Test update timestamp
    original_updated_at = asset.updated_at
    await db_session.refresh(asset)
    asset.path = "/new/path"
    await db_session.commit()

    assert asset.updated_at > original_updated_at
    assert asset.created_at == asset.created_at  # Should not change


@pytest.mark.asyncio
async def test_asset_enum_validation(db_session: AsyncSession) -> None:
    """Test that asset_type must be a valid enum value."""
    project = Project(id=uuid.uuid4(), topic="Test Topic", status=ProjectStatus.CREATED)
    db_session.add(project)
    await db_session.commit()
    # Test valid asset types
    valid_types = ["script", "narration", "video", "image", "slide"]
    for asset_type in valid_types:
        asset = Asset(
            id=uuid.uuid4(),
            project_id=project.id,
            asset_type=asset_type,
            path=f"/path/to/{asset_type}",
        )
        db_session.add(asset)
        await db_session.commit()  # Commit each successful creation
        result = await db_session.execute(select(Asset).filter_by(id=asset.id))
        saved_asset = result.scalar_one()
        assert saved_asset.asset_type == asset_type
        await db_session.delete(asset)  # cleanup
        await db_session.commit()  # Commit after each successful creation
    # Test invalid asset type
    with pytest.raises(DBAPIError):
        invalid_asset = Asset(
            id=uuid.uuid4(),
            project_id=project.id,
            asset_type="invalid_type",
            path="/path/to/asset",
        )
        db_session.add(invalid_asset)
        await db_session.commit()


@pytest.mark.asyncio
async def test_asset_path_not_nullable(db_session: AsyncSession) -> None:
    """Test that path cannot be null."""
    project = Project(id=uuid.uuid4(), topic="Test Topic", status=ProjectStatus.CREATED)
    db_session.add(project)
    await db_session.commit()
    with pytest.raises(IntegrityError):
        asset = Asset(
            id=uuid.uuid4(),
            project_id=project.id,
            asset_type="script",
            path=None,  # This should raise an error
        )
        db_session.add(asset)
        await db_session.commit()
