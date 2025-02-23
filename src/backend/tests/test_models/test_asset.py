import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.models.asset import Asset
from src.backend.models.project import Project
from src.backend.schemas.project import ProjectStatus

@pytest.mark.asyncio
async def test_create_asset(db_session: AsyncSession) -> None:
    """Test creating an asset with valid data."""
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
    await db_session.refresh(asset)

    # Update the asset
    asset.path = "/updated/path"
    asset.asset_type = "video"
    await db_session.commit()

    # Verify with query
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

    await db_session.refresh(asset) # Important: Get *exact* time from DB
    assert asset.created_at >= start_time
    assert asset.updated_at >= start_time

    # Test update timestamp
    original_updated_at = asset.updated_at  # Store original time
    asset.path = "/new/path" #modify
    await db_session.commit()
    await db_session.refresh(asset) #refresh after update

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
        asset = Asset(id=uuid.uuid4(), project_id=project.id, asset_type=asset_type, path=f"/path/to/{asset_type}")
        db_session.add(asset)
        await db_session.commit()
        await db_session.refresh(asset) #refresh after each successful creation
        assert asset.asset_type == asset_type
        await db_session.delete(asset)  # cleanup
        await db_session.commit() # Commit after each successful creation

    # Test invalid asset type
    with pytest.raises(IntegrityError):
        invalid_asset = Asset(
            id=uuid.uuid4(),
            project_id=project.id,
            asset_type="invalid_type",  # Invalid value
            path="/path/to/asset",
        )
        db_session.add(invalid_asset)
        await db_session.commit()  # This should raise IntegrityError


@pytest.mark.asyncio
async def test_asset_path_not_nullable(db_session: AsyncSession) -> None:
    """Test that path cannot be null."""
    project = Project(id=uuid.uuid4(), topic="Test Topic", status=ProjectStatus.CREATED)
    db_session.add(project)
    await db_session.commit()
    with pytest.raises(IntegrityError):
        asset = Asset(
            id=uuid.uuid4(), project_id=project.id, asset_type="script", path=None
        )
        db_session.add(asset)
        await db_session.commit()
