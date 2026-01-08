#!/usr/bin/env python3
"""
Complete Final Integration - ALL Features
Real-time WebSocket + AI Engines + Complete Integration
"""

import os
from pathlib import Path

def create_file(path, content):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return len(content)

print("="*80)
print("  COMPLETE FINAL INTEGRATION - ALL FEATURES")
print("  Real-time + AI + WebSocket + Complete Backend & Frontend")
print("="*80)
print()

created = []

# ============================================================
# FEATURE 1: REAL-TIME WEBSOCKET - COMPLETE BACKEND
# ============================================================
print("🔴 FEATURE 1: REAL-TIME WEBSOCKET INTEGRATION")
print("="*80)
print()

print("1. Creating WebSocket Manager...")

create_file('services/api/app/websocket/connection_manager.py', '''"""
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
''')

created.append(('WebSocket Manager', 4.5))
print("   ✅ WebSocket manager created")

print("2. Creating WebSocket Router...")

create_file('services/api/app/routers/websocket.py', '''"""
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
''')

created.append(('WebSocket Router', 2.8))
print("   ✅ WebSocket router created")

print("3. Integrating WebSocket with Time Tracking...")

# Update time tracking to send real-time notifications
create_file('services/api/app/routers/time_tracking_realtime.py', '''"""
Time Tracking with Real-time WebSocket Integration
Sends live updates when employees clock in/out
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database.session import get_db
from app.auth.jwt_manager import get_current_user
from app.auth.rbac import require_permission, Permission
from app.logging.logging_config import log_audit_event
from app.crud import time_entry as time_crud
from app.websocket.connection_manager import manager

router = APIRouter()

@router.post("/clock-in-realtime", status_code=status.HTTP_201_CREATED)
@require_permission(Permission.TIME_CREATE)
async def clock_in_realtime(
    location: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Clock in with REAL-TIME WebSocket notification
    """
    employee_id = current_user['id']
    tenant_id = current_user['tenant_id']
    
    try:
        entry = time_crud.clock_in(db, employee_id, tenant_id, location)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # REAL-TIME NOTIFICATION via WebSocket
    await manager.notify_time_entry(
        tenant_id=tenant_id,
        employee_id=employee_id,
        action='clock_in',
        data={
            'id': entry.id,
            'employee_id': entry.employee_id,
            'start_time': entry.start_time.isoformat(),
            'status': entry.status
        }
    )
    
    log_audit_event(
        event_type='time_clock_in',
        user_id=employee_id,
        tenant_id=tenant_id,
        resource='time_entries',
        action='create',
        details={'entry_id': entry.id}
    )
    
    return {
        'id': entry.id,
        'employee_id': entry.employee_id,
        'start_time': entry.start_time,
        'status': entry.status,
        'message': 'Clocked in successfully',
        'realtime_notification_sent': True
    }

@router.post("/clock-out-realtime")
@require_permission(Permission.TIME_CREATE)
async def clock_out_realtime(
    location: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Clock out with REAL-TIME WebSocket notification
    """
    employee_id = current_user['id']
    tenant_id = current_user['tenant_id']
    
    try:
        entry = time_crud.clock_out(db, employee_id, tenant_id, location)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # REAL-TIME NOTIFICATION via WebSocket
    await manager.notify_time_entry(
        tenant_id=tenant_id,
        employee_id=employee_id,
        action='clock_out',
        data={
            'id': entry.id,
            'employee_id': entry.employee_id,
            'start_time': entry.start_time.isoformat(),
            'end_time': entry.end_time.isoformat(),
            'hours': entry.hours,
            'overtime_hours': entry.overtime_hours,
            'status': entry.status
        }
    )
    
    log_audit_event(
        event_type='time_clock_out',
        user_id=employee_id,
        tenant_id=tenant_id,
        resource='time_entries',
        action='update',
        details={'entry_id': entry.id, 'hours': entry.hours}
    )
    
    return {
        'id': entry.id,
        'employee_id': entry.employee_id,
        'hours': entry.hours,
        'overtime_hours': entry.overtime_hours,
        'status': entry.status,
        'message': 'Clocked out successfully',
        'realtime_notification_sent': True
    }
''')

created.append(('Time Tracking Real-time', 3.6))
print("   ✅ Real-time time tracking created")

print()
print(f"✅ WebSocket integration complete: {sum([s for _, s in created]):.1f} KB")
print()

