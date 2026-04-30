from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from nexiss.api.deps.auth import resolve_auth_context_from_token
from nexiss.db.session import AsyncSessionFactory
from nexiss.services.realtime.progress_events import subscribe_progress_events

router = APIRouter(prefix="/realtime", tags=["realtime"])


@router.websocket("/progress/ws")
async def progress_websocket(websocket: WebSocket) -> None:
    token = websocket.query_params.get("token")
    org_id_raw = websocket.query_params.get("org_id")
    if not token or not org_id_raw:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="token and org_id are required")
        return
    try:
        org_id = UUID(org_id_raw)
    except ValueError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="invalid org_id")
        return

    async with AsyncSessionFactory() as db:
        try:
            auth = await resolve_auth_context_from_token(token, db)
        except Exception:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="auth failed")
            return
        if org_id not in auth.memberships:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="org access denied")
            return

    await websocket.accept()
    await websocket.send_json({"event": "connected", "org_id": str(org_id)})
    try:
        async for event in subscribe_progress_events(org_id):
            await websocket.send_json(event)
    except WebSocketDisconnect:
        return
