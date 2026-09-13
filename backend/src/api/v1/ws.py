"""WebSocket real-time collaboration endpoint."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(prefix="/ws", tags=["Collaboration"])


@router.websocket("/{workspace_id}")
async def websocket_endpoint(websocket: WebSocket, workspace_id: str):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            await websocket.send_json({"echo": data, "workspace_id": workspace_id})
    except WebSocketDisconnect:
        pass
