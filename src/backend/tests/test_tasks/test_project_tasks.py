import uuid
from unittest.mock import MagicMock, patch

import pytest
import redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.models.project import Project
from src.backend.schemas.project import ProjectStatus
from src.backend.tasks.project_tasks import celery_debug_task as test_task
from src.backend.tasks.project_tasks import process_project, redis_interaction_test


@pytest.fixture(scope="session")
def celery_config():
    """Celery test configuration that uses in-memory broker and backend."""
    return {
        "broker_url": "memory://",
        "result_backend": "cache+memory://",
        "task_always_eager": True,  # Tasks will be executed locally/synchronously
        "task_eager_propagates": True,  # Exceptions will be propagated
        "worker_send_task_events": False,  # Disable unnecessary events for testing
        "task_send_sent_event": False,
        "broker_connection_retry": False,  # Don't retry connections
        "broker_connection_max_retries": 0,
    }


@pytest.fixture(autouse=True)
def setup_celery_app():
    """Setup celery app with test config for each test."""
    from src.backend.tasks import celery_app

    celery_app.conf.update(
        broker_url="memory://",
        result_backend="cache+memory://",
        task_always_eager=True,
        task_eager_propagates=True,
    )
    return celery_app


@pytest.mark.celery
def test_test_task():
    """Test the basic test_task functionality"""
    result = test_task.delay(2, 3)
    assert result.get() == 5
    assert result.successful()


@pytest.mark.celery
def test_redis_interaction_test_success():
    """Test successful Redis interaction"""
    with patch("redis.Redis") as mock_redis:
        # Setup mock Redis instance
        mock_instance = MagicMock()
        mock_instance.ping.return_value = True
        mock_instance.set.return_value = True
        mock_instance.get.return_value = "testvalue"
        mock_instance.info.return_value = {
            "redis_version": "7.0.0",
            "connected_clients": "1",
            "used_memory_human": "1.2M",
        }
        mock_redis.return_value = mock_instance

        result = redis_interaction_test.delay()
        assert result.get() == "Success"
        assert result.successful()


@pytest.mark.celery
def test_redis_interaction_test_auth_failure():
    """Test Redis authentication failure"""
    with patch("redis.Redis") as mock_redis:
        mock_redis.side_effect = redis.AuthenticationError("Invalid password")
        result = redis_interaction_test.delay()
        assert "Auth Error" in result.get()
        assert result.successful()  # Task completes but returns error message


@pytest.mark.celery
def test_redis_interaction_test_connection_failure():
    """Test Redis connection failure"""
    with patch("redis.Redis") as mock_redis:
        mock_redis.side_effect = redis.ConnectionError("Connection refused")
        result = redis_interaction_test.delay()
        assert "Connection Error" in result.get()
        assert result.successful()  # Task completes but returns error message


@pytest.mark.asyncio
@pytest.mark.celery
async def test_process_project_task_success(db_session: AsyncSession):
    """Test successful project processing"""
    # Create test project
    project = Project(id=uuid.uuid4(), topic="Test Topic", status=ProjectStatus.CREATED)
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    # Run task
    result = process_project.delay(str(project.id))
    assert result.successful()

    # Verify status changes
    await db_session.refresh(project)
    assert project.status == ProjectStatus.COMPLETED


@pytest.mark.asyncio
@pytest.mark.celery
async def test_process_project_task_not_found(db_session: AsyncSession):
    """Test process_project with non-existent project ID"""
    non_existent_id = str(uuid.uuid4())
    result = process_project.delay(non_existent_id)
    assert result.successful()  # Task should complete without error


@pytest.mark.asyncio
@pytest.mark.celery
async def test_process_project_task_db_error(db_session: AsyncSession):
    """Test process_project handling of database errors"""
    # Create test project
    project = Project(id=uuid.uuid4(), topic="Test Topic", status=ProjectStatus.CREATED)
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    # Simulate database error during processing
    with patch("sqlalchemy.ext.asyncio.AsyncSession.commit") as mock_commit:
        mock_commit.side_effect = Exception("Database error")

        # Run task and expect it to handle the error
        result = process_project.delay(str(project.id))
        # Wait for task completion
        try:
            result.get()
        except Exception:
            pass  # Expected exception from task

        # Verify project status is set to ERROR
        await db_session.refresh(project)
        assert project.status == ProjectStatus.ERROR
