# app/websockets/manager.py

from typing import List
from fastapi import WebSocket
from asyncio import Lock
import asyncio


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._lock = Lock()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        async with self._lock:
            self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        async with self._lock:
            to_remove = []
            for ws in self.active_connections:
                try:
                    await ws.send_json(message)
                except Exception:
                    to_remove.append(ws)

            for ws in to_remove:
                if ws in self.active_connections:
                    self.active_connections.remove(ws)

    # ⭐ NEW: sync-safe wrapper for workers
    def broadcast_sync(self, message: dict):
        """
        Safe to call from synchronous worker code.
        Detects whether an event loop is running and handles accordingly.
        """
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # Running inside FastAPI event loop
            loop.create_task(self.broadcast(message))
        else:
            # Running in a worker thread/process
            asyncio.run(self.broadcast(message))


manager = ConnectionManager()
