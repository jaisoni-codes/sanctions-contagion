from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import asyncio

router = APIRouter()

clients = set()

@router.websocket("/ws/events")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)
    try:
        while True:
            # Keep connection open and wait for messages or just ping/pong
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        clients.remove(websocket)

async def broadcast_event(event_type: str, payload: dict):
    message = json.dumps({
        "type": event_type,
        "payload": payload
    })
    for client in clients:
        try:
            await client.send_text(message)
        except:
            pass
