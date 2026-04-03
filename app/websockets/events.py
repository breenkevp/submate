# app/websockets/events.py

import asyncio
from datetime import datetime, timezone
from app.websockets.manager import manager


def broadcast_event(event_type: str, payload: dict):
    """
    Unified event emitter for all websocket events.
    Adds timestamp and wraps payload in a consistent schema.
    """

    message = {
        "type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
    }

    try:
        asyncio.create_task(manager.broadcast(message))
    except RuntimeError:
        # No running event loop (e.g., worker started in sync mode)
        pass
