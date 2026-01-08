"""
WebSocket Manager
Real-time updates for time tracking, notifications, live dashboards
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Set
import json
import logging
import asyncio

logger = logging.getLogger(__name__)

class ConnectionManager:
    """
    Manages WebSocket connections
    Supports rooms for multi-tenant isolation
    """
    
    def __init__(self):
        # Active connections per room
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # User to connection mapping
        self.user_connections: Dict[int, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, room: str, user_id: int):
        """Accept new WebSocket connection"""
        await websocket.accept()
        
        # Add to room
        if room not in self.active_connections:
            self.active_connections[room] = set()
        self.active_connections[room].add(websocket)
        
        # Map user to connection
        self.user_connections[user_id] = websocket
        
        logger.info(f"WebSocket connected: user={user_id}, room={room}")
    
    def disconnect(self, websocket: WebSocket, room: str, user_id: int):
        """Remove WebSocket connection"""
        if room in self.active_connections:
            self.active_connections[room].discard(websocket)
            
            # Remove empty rooms
            if not self.active_connections[room]:
                del self.active_connections[room]
        
        # Remove user mapping
        if user_id in self.user_connections:
            del self.user_connections[user_id]
        
        logger.info(f"WebSocket disconnected: user={user_id}, room={room}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to specific connection"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Failed to send personal message: {e}")
    
    async def broadcast_to_room(self, message: dict, room: str):
        """Broadcast message to all connections in room"""
        if room not in self.active_connections:
            return
        
        disconnected = []
        
        for connection in self.active_connections[room]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to broadcast to room: {e}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.active_connections[room].discard(connection)
    
    async def send_to_user(self, message: dict, user_id: int):
        """Send message to specific user"""
        if user_id in self.user_connections:
            websocket = self.user_connections[user_id]
            await self.send_personal_message(message, websocket)
    
    def get_room_size(self, room: str) -> int:
        """Get number of connections in room"""
        return len(self.active_connections.get(room, set()))

# Global connection manager
manager = ConnectionManager()

# Real-time event types
class RealtimeEvents:
    """Event types for real-time updates"""
    
    # Time tracking events
    CLOCK_IN = "clock_in"
    CLOCK_OUT = "clock_out"
    TIME_ENTRY_UPDATE = "time_entry_update"
    
    # Notification events
    NOTIFICATION = "notification"
    ALERT = "alert"
    
    # Dashboard events
    DASHBOARD_UPDATE = "dashboard_update"
    METRICS_UPDATE = "metrics_update"
    
    # Team events
    TEAM_MEMBER_ONLINE = "team_member_online"
    TEAM_MEMBER_OFFLINE = "team_member_offline"
    
    # System events
    SYSTEM_MAINTENANCE = "system_maintenance"
    SYSTEM_UPDATE = "system_update"

async def broadcast_clock_in(tenant_id: int, employee_id: int, employee_name: str):
    """Broadcast clock-in event to team"""
    message = {
        'event': RealtimeEvents.CLOCK_IN,
        'employee_id': employee_id,
        'employee_name': employee_name,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    room = f"tenant_{tenant_id}"
    await manager.broadcast_to_room(message, room)

async def send_notification(user_id: int, notification_data: dict):
    """Send real-time notification to user"""
    message = {
        'event': RealtimeEvents.NOTIFICATION,
        'data': notification_data
    }
    
    await manager.send_to_user(message, user_id)

async def broadcast_dashboard_update(tenant_id: int, metrics: dict):
    """Broadcast dashboard metrics update"""
    message = {
        'event': RealtimeEvents.DASHBOARD_UPDATE,
        'metrics': metrics
    }
    
    room = f"tenant_{tenant_id}_dashboard"
    await manager.broadcast_to_room(message, room)
