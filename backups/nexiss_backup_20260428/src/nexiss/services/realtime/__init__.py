import json
from typing import Any
import redis.asyncio as aioredis

from nexiss.core.config import settings


class RealtimeService:
    """Publishes processing progress events to Redis pub/sub.
    The WebSocket endpoint subscribes to these channels."""

    def __init__(self):
        self.redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)

    def _channel(self, document_id: str) -> str:
        return f"nexiss:progress:{document_id}"

    async def publish_progress(
        self,
        document_id: str,
        step: str,
        progress_pct: int,
        status: str = 'processing',
        error: str | None = None,
    ) -> None:
        payload = json.dumps({
            'document_id': document_id,
            'step': step,
            'progress_pct': progress_pct,
            'status': status,
            'error': error,
        })
        await self.redis.publish(self._channel(document_id), payload)

    async def subscribe(self, document_id: str):
        """Async generator yielding progress payloads for a document."""
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(self._channel(document_id))
        try:
            async for message in pubsub.listen():
                if message['type'] == 'message':
                    yield json.loads(message['data'])
        finally:
            await pubsub.unsubscribe(self._channel(document_id))
            await pubsub.close()


realtime_service = RealtimeService()
