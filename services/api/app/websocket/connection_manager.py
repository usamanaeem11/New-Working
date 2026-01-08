"""
WebSocket Connection Manager - REAL IMPLEMENTATION
Live updates, presence tracking, notifications
"""

from fastapi import WebSocket
from typing import Dict, List, Set
import json
import asyncio
from datetime import datetime

class ConnectionManager:
    """
    Manage WebSocket connections for real-time updates
    """
    
    def __init__(self):
        # Active connections by tenant
        self.active_connections: Dict[int, Dict[int, WebSocket]] = {}
        # User presence tracking
        self.user_presence: Dict[int, Set[int]] = {}
        
    async def connect(self, websocket: WebSocket, user_id: int, tenant_id: int):
        """Accept and register WebSocket connection"""
        await websocket.accept()
        
        # Initialize tenant connections if needed
        if tenant_id not in self.active_connections:
            self.active_connections[tenant_id] = {}
            self.user_presence[tenant_id] = set()
        
        # Register connection
        self.active_connections[tenant_id][user_id] = websocket
        self.user_presence[tenant_id].add(user_id)
        
        # Broadcast user joined
        await self.broadcast_to_tenant(
            tenant_id,
            {
                'type': 'user_presence',
                'action': 'joined',
                'user_id': user_id,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
    
    def disconnect(self, user_id: int, tenant_id: int):
        """Remove WebSocket connection"""
        if tenant_id in self.active_connections:
            if user_id in self.active_connections[tenant_id]:
                del self.active_connections[tenant_id][user_id]
            
            if user_id in self.user_presence[tenant_id]:
                self.user_presence[tenant_id].remove(user_id)
    
    async def send_personal_message(self, message: dict, user_id: int, tenant_id: int):
        """Send message to specific user"""
        if tenant_id in self.active_connections:
            if user_id in self.active_connections[tenant_id]:
                websocket = self.active_connections[tenant_id][user_id]
                await websocket.send_json(message)
    
    async def broadcast_to_tenant(self, tenant_id: int, message: dict):
        """Broadcast message to all users in tenant"""
        if tenant_id not in self.active_connections:
            return
        
        disconnected = []
        for user_id, websocket in self.active_connections[tenant_id].items():
            try:
                await websocket.send_json(message)
            except Exception as e:
                print(f"Error sending to user {user_id}: {e}")
                disconnected.append(user_id)
        
        # Remove disconnected users
        for user_id in disconnected:
            self.disconnect(user_id, tenant_id)
    
    async def notify_time_entry(self, tenant_id: int, employee_id: int, action: str, data: dict):
        """Send real-time time entry notification"""
        message = {
            'type': 'time_entry',
            'action': action,  # 'clock_in', 'clock_out'
            'employee_id': employee_id,
            'data': data,
            'timestamp': datetime.utcnow().isoformat()
        }
        await self.broadcast_to_tenant(tenant_id, message)
    
    async def notify_payroll_complete(self, tenant_id: int, payroll_run_id: int, data: dict):
        """Send payroll completion notification"""
        message = {
            'type': 'payroll',
            'action': 'completed',
            'payroll_run_id': payroll_run_id,
            'data': data,
            'timestamp': datetime.utcnow().isoformat()
        }
        await self.broadcast_to_tenant(tenant_id, message)
    
    async def notify_employee_update(self, tenant_id: int, employee_id: int, action: str):
        """Send employee update notification"""
        message = {
            'type': 'employee',
            'action': action,  # 'created', 'updated', 'deleted'
            'employee_id': employee_id,
            'timestamp': datetime.utcnow().isoformat()
        }
        await self.broadcast_to_tenant(tenant_id, message)
    
    def get_online_users(self, tenant_id: int) -> List[int]:
        """Get list of online users for tenant"""
        return list(self.user_presence.get(tenant_id, set()))

# Global instance
manager = ConnectionManager()
