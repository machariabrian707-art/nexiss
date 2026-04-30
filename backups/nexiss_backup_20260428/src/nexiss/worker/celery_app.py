from celery import Celery
from celery.signals import task_failure, task_postrun, task_prerun

from nexiss.core.config import get_settings
from nexiss.core.metrics import celery_tasks_total

settings = get_settings()

celery_app = Celery(
    "nexiss",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["nexiss.worker.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_always_eager=settings.celery_task_always_eager,
    task_eager_propagates=True,
)


@task_prerun.connect
def _task_prerun(*, task=None, task_id=None, **_kwargs):  # type: ignore[no-untyped-def]
    _ = (task, task_id)


@task_postrun.connect
def _task_postrun(*, task=None, state=None, **_kwargs):  # type: ignore[no-untyped-def]
    if task and state:
        celery_tasks_total.labels(task.name, str(state).lower()).inc()


@task_failure.connect
def _task_failure(*, sender=None, **_kwargs):  # type: ignore[no-untyped-def]
    if sender:
        celery_tasks_total.labels(sender.name, "failed").inc()
