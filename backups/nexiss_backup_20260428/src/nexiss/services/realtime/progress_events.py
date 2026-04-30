from __future__ import annotations

import json
from collections.abc import AsyncGenerator
from uuid import UUID

import redis
from redis.asyncio import Redis as AsyncRedis

from nexiss.core.config import get_settings
from nexiss.db.models.processing_job import ProcessingJob, ProcessingJobStatus

settings = get_settings()


def progress_channel_name(org_id: UUID) -> str:
    return f"{settings.realtime_progress_channel_prefix}:{org_id}"


def build_progress_event(job: ProcessingJob) -> dict[str, str | int | None]:
    return {
        "event": "document_progress",
        "org_id": str(job.org_id),
        "job_id": str(job.id),
        "document_id": str(job.document_id),
        "task_id": job.task_id,
        "status": job.status.value if isinstance(job.status, ProcessingJobStatus) else str(job.status),
        "progress_percentage": int(job.progress_percentage),
        "current_step": job.current_step,
        "error_message": job.error_message,
    }


def publish_progress_event(job: ProcessingJob) -> None:
    client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
    try:
        client.publish(progress_channel_name(job.org_id), json.dumps(build_progress_event(job)))
    finally:
        client.close()


async def subscribe_progress_events(org_id: UUID) -> AsyncGenerator[dict, None]:
    client = AsyncRedis.from_url(settings.redis_url, decode_responses=True)
    pubsub = client.pubsub()
    channel = progress_channel_name(org_id)
    await pubsub.subscribe(channel)
    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message is None:
                continue
            data = message.get("data")
            if not isinstance(data, str):
                continue
            yield json.loads(data)
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.close()
        await client.aclose()
