"""
WebSocket Router - REAL IMPLEMENTATION
Real-time updates endpoint
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.websocket.connection_manager import manager
from app.auth.jwt_manager import decode_token
import json

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str):
    """
    WebSocket endpoint for real-time updates
    Handles: presence, time entries, payroll, notifications
    """
    
    # Authenticate
    try:
        payload = decode_token(token)
        user_id = payload['user_id']
        tenant_id = payload['tenant_id']
    except Exception as e:
        await websocket.close(code=1008, reason="Authentication failed")
        return
    
    # Connect
    await manager.connect(websocket, user_id, tenant_id)
    
    # Send initial connection success
    await websocket.send_json({
        'type': 'connection',
        'status': 'connected',
        'user_id': user_id,
        'tenant_id': tenant_id
    })
    
    # Send online users
    online_users = manager.get_online_users(tenant_id)
    await websocket.send_json({
        'type': 'presence',
        'online_users': online_users
    })
    
    try:
        # Keep connection alive and handle messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get('type') == 'ping':
                await websocket.send_json({'type': 'pong'})
            
            elif message.get('type') == 'broadcast':
                # Broadcast to all users in tenant
                await manager.broadcast_to_tenant(
                    tenant_id,
                    {
                        'type': 'message',
                        'from_user_id': user_id,
                        'message': message.get('message')
                    }
                )
    
    except WebSocketDisconnect:
        manager.disconnect(user_id, tenant_id)
        # Notify others user left
        await manager.broadcast_to_tenant(
            tenant_id,
            {
                'type': 'user_presence',
                'action': 'left',
                'user_id': user_id
            }
        )
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(user_id, tenant_id)
