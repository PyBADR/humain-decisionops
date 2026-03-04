"""WebSocket endpoints for real-time updates."""
import asyncio
import json
from datetime import datetime
from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import structlog

logger = structlog.get_logger()

router = APIRouter(tags=["websocket"])

# Connection managers
class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        # Global connections for broadcast
        self.active_connections: Set[WebSocket] = set()
        # Claim-specific connections
        self.claim_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, claim_id: str = None):
        await websocket.accept()
        self.active_connections.add(websocket)
        
        if claim_id:
            if claim_id not in self.claim_connections:
                self.claim_connections[claim_id] = set()
            self.claim_connections[claim_id].add(websocket)
        
        logger.info("websocket_connected", claim_id=claim_id)
    
    def disconnect(self, websocket: WebSocket, claim_id: str = None):
        self.active_connections.discard(websocket)
        
        if claim_id and claim_id in self.claim_connections:
            self.claim_connections[claim_id].discard(websocket)
            if not self.claim_connections[claim_id]:
                del self.claim_connections[claim_id]
        
        logger.info("websocket_disconnected", claim_id=claim_id)
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients."""
        message["timestamp"] = datetime.utcnow().isoformat()
        data = json.dumps(message)
        
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_text(data)
            except Exception:
                disconnected.add(connection)
        
        # Clean up disconnected
        for conn in disconnected:
            self.active_connections.discard(conn)
    
    async def send_to_claim(self, claim_id: str, message: dict):
        """Send message to all clients watching a specific claim."""
        if claim_id not in self.claim_connections:
            return
        
        message["timestamp"] = datetime.utcnow().isoformat()
        data = json.dumps(message)
        
        disconnected = set()
        for connection in self.claim_connections[claim_id]:
            try:
                await connection.send_text(data)
            except Exception:
                disconnected.add(connection)
        
        # Clean up disconnected
        for conn in disconnected:
            self.claim_connections[claim_id].discard(conn)


# Global connection manager instance
manager = ConnectionManager()


@router.websocket("/ws/updates")
async def websocket_global_updates(websocket: WebSocket):
    """WebSocket endpoint for global updates (new claims, decisions, etc.)."""
    await manager.connect(websocket)
    
    try:
        while True:
            # Keep connection alive and listen for any client messages
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                # Echo back or handle client messages if needed
                await websocket.send_json({
                    "type": "ack",
                    "payload": {"received": data},
                    "timestamp": datetime.utcnow().isoformat()
                })
            except asyncio.TimeoutError:
                # Send heartbeat
                await websocket.send_json({
                    "type": "heartbeat",
                    "payload": {},
                    "timestamp": datetime.utcnow().isoformat()
                })
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error("websocket_error", error=str(e))
        manager.disconnect(websocket)


@router.websocket("/ws/claims/{claim_id}")
async def websocket_claim_updates(websocket: WebSocket, claim_id: str):
    """WebSocket endpoint for claim-specific updates."""
    await manager.connect(websocket, claim_id)
    
    try:
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                await websocket.send_json({
                    "type": "ack",
                    "payload": {"claim_id": claim_id, "received": data},
                    "timestamp": datetime.utcnow().isoformat()
                })
            except asyncio.TimeoutError:
                # Send heartbeat
                await websocket.send_json({
                    "type": "heartbeat",
                    "payload": {"claim_id": claim_id},
                    "timestamp": datetime.utcnow().isoformat()
                })
    except WebSocketDisconnect:
        manager.disconnect(websocket, claim_id)
    except Exception as e:
        logger.error("websocket_error", claim_id=claim_id, error=str(e))
        manager.disconnect(websocket, claim_id)


# Helper functions to broadcast events from other parts of the application
async def broadcast_new_claim(claim_data: dict):
    """Broadcast new claim event to all connected clients."""
    await manager.broadcast({
        "type": "new_claim",
        "payload": claim_data
    })


async def broadcast_new_decision(decision_data: dict):
    """Broadcast new decision event to all connected clients."""
    await manager.broadcast({
        "type": "new_decision",
        "payload": decision_data
    })


async def broadcast_claim_status_update(claim_id: str, status: str):
    """Broadcast claim status update to clients watching this claim."""
    await manager.send_to_claim(claim_id, {
        "type": "status_update",
        "payload": {"claim_id": claim_id, "status": status}
    })


async def broadcast_pipeline_progress(claim_id: str, node: str, progress: float):
    """Broadcast pipeline progress to clients watching this claim."""
    await manager.send_to_claim(claim_id, {
        "type": "pipeline_progress",
        "payload": {"claim_id": claim_id, "node": node, "progress": progress}
    })
