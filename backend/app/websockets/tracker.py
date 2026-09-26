import asyncio
import json
from fastapi import WebSocket, WebSocketDisconnect

from app.core.redis import redis_client


class ConnectionManager:
    def __init__(self):
        self.active: dict[int, list[WebSocket]] = {}

    async def connect(self, order_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active.setdefault(order_id, []).append(websocket)

    def disconnect(self, order_id: int, websocket: WebSocket):
        connections = self.active.get(order_id, [])
        if websocket in connections:
            connections.remove(websocket)
        if not connections:
            self.active.pop(order_id, None)

    async def broadcast_to_order(self, order_id: int, message: dict):
        connections = self.active.get(order_id, [])
        dead = []
        for ws in connections:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(order_id, ws)


manager = ConnectionManager()


async def listen_for_updates():
    pubsub = redis_client.pubsub()
    await pubsub.subscribe("order_updates", "driver_locations")

    async for message in pubsub.listen():
        if message["type"] != "message":
            continue

        channel = message["channel"]
        data = message["data"]

        if channel == "order_updates":
            order_id_str, status = data.split(":", 1)
            order_id = int(order_id_str)
            await manager.broadcast_to_order(order_id, {
                "type": "status_update",
                "order_id": order_id,
                "status": status,
            })

        elif channel == "driver_locations":
            parts = data.split(":")
            driver_id, lat, lng = int(parts[0]), float(parts[1]), float(parts[2])
            for order_id, connections in manager.active.items():
                if connections:
                    await manager.broadcast_to_order(order_id, {
                        "type": "driver_location",
                        "driver_id": driver_id,
                        "latitude": lat,
                        "longitude": lng,
                    })


async def websocket_endpoint(websocket: WebSocket, order_id: int):
    await manager.connect(order_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(order_id, websocket)
