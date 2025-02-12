from celery import Celery

celery = Celery(
    'project_tasks',
    broker='redis://redis:6379/0',
    backend='redis://redis:6379/0',
)

@celery.task(name='test_task')
def test_task(x, y):
    return x + y