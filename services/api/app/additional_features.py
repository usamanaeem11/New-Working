"""
Additional Critical Features
Includes: Kanban Board, Subtasks, Recurring Tasks, Templates, Shift Management, 2FA
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import uuid
import pyotp
import qrcode
import io
import base64

router = APIRouter(prefix="/api/features", tags=["Additional Features"])

# ============================================
# KANBAN BOARD
# ============================================

class KanbanColumn(BaseModel):
    id: Optional[str] = None
    name: str
    position: int
    project_id: str
    color: Optional[str] = "#3B82F6"

class KanbanCard(BaseModel):
    task_id: str
    column_id: str
    position: int

@router.get("/kanban/{project_id}")
async def get_kanban_board(
    project_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get Kanban board for project"""
    try:
        # Get columns
        columns = await db.table('kanban_columns').select('*')\
            .eq('project_id', project_id)\
            .order('position')\
            .execute()
        
        # Get tasks for each column
        kanban_data = []
        for column in columns.data:
            tasks = await db.table('tasks').select('*')\
                .eq('project_id', project_id)\
                .eq('status', column['name'].lower().replace(' ', '_'))\
                .execute()
            
            kanban_data.append({
                "column": column,
                "tasks": tasks.data
            })
        
        return {
            "success": True,
            "kanban_board": kanban_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/kanban/column")
async def create_kanban_column(
    column: KanbanColumn,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create Kanban column"""
    try:
        column_id = str(uuid.uuid4())
        await db.table('kanban_columns').insert({
            "id": column_id,
            "project_id": column.project_id,
            "name": column.name,
            "position": column.position,
            "color": column.color,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        return {
            "success": True,
            "column_id": column_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/kanban/move")
async def move_kanban_card(
    card: KanbanCard,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Move task between Kanban columns"""
    try:
        # Get column name
        column = await db.table('kanban_columns').select('*')\
            .eq('id', card.column_id).single().execute()
        
        # Update task status
        await db.table('tasks').update({
            "status": column.data['name'].lower().replace(' ', '_'),
            "kanban_position": card.position,
            "updated_at": datetime.utcnow().isoformat()
        }).eq('id', card.task_id).execute()
        
        return {
            "success": True,
            "message": "Card moved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# SUBTASKS
# ============================================

class SubtaskCreate(BaseModel):
    parent_task_id: str
    title: str
    estimated_minutes: Optional[int] = None

@router.post("/subtasks")
async def create_subtask(
    subtask: SubtaskCreate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create subtask"""
    try:
        subtask_id = str(uuid.uuid4())
        await db.table('subtasks').insert({
            "id": subtask_id,
            "parent_task_id": subtask.parent_task_id,
            "title": subtask.title,
            "estimated_minutes": subtask.estimated_minutes,
            "is_completed": False,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        return {
            "success": True,
            "subtask_id": subtask_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/subtasks/{task_id}")
async def get_subtasks(
    task_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get all subtasks for a task"""
    try:
        subtasks = await db.table('subtasks').select('*')\
            .eq('parent_task_id', task_id)\
            .execute()
        
        return {
            "success": True,
            "subtasks": subtasks.data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/subtasks/{subtask_id}/complete")
async def complete_subtask(
    subtask_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Mark subtask as complete"""
    try:
        await db.table('subtasks').update({
            "is_completed": True,
            "completed_at": datetime.utcnow().isoformat()
        }).eq('id', subtask_id).execute()
        
        return {
            "success": True,
            "message": "Subtask completed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# RECURRING TASKS
# ============================================

class RecurringTaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    project_id: str
    assigned_to_id: Optional[str] = None
    recurrence_type: str  # daily, weekly, monthly
    recurrence_interval: int = 1
    recurrence_days: Optional[List[int]] = None  # For weekly (0=Mon, 6=Sun)
    start_date: datetime
    end_date: Optional[datetime] = None

@router.post("/recurring-tasks")
async def create_recurring_task(
    recurring_task: RecurringTaskCreate,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create recurring task"""
    try:
        recurring_task_id = str(uuid.uuid4())
        
        await db.table('recurring_tasks').insert({
            "id": recurring_task_id,
            "title": recurring_task.title,
            "description": recurring_task.description,
            "project_id": recurring_task.project_id,
            "assigned_to_id": recurring_task.assigned_to_id,
            "recurrence_type": recurring_task.recurrence_type,
            "recurrence_interval": recurring_task.recurrence_interval,
            "recurrence_days": recurring_task.recurrence_days,
            "start_date": recurring_task.start_date.isoformat(),
            "end_date": recurring_task.end_date.isoformat() if recurring_task.end_date else None,
            "is_active": True,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        # Generate first instance
        background_tasks.add_task(
            generate_recurring_task_instances,
            recurring_task_id
        )
        
        return {
            "success": True,
            "recurring_task_id": recurring_task_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def generate_recurring_task_instances(recurring_task_id: str):
    """Background task to generate recurring task instances"""
    # Get recurring task
    db = get_db()
    recurring = await db.table('recurring_tasks').select('*')\
        .eq('id', recurring_task_id).single().execute()
    
    if not recurring.data:
        return
    
    task_data = recurring.data
    start_date = datetime.fromisoformat(task_data['start_date'])
    end_date = datetime.fromisoformat(task_data['end_date']) if task_data['end_date'] else start_date + timedelta(days=365)
    
    current_date = start_date
    instances_created = 0
    
    while current_date <= end_date and instances_created < 52:  # Max 52 instances
        # Create task instance
        await db.table('tasks').insert({
            "id": str(uuid.uuid4()),
            "recurring_task_id": recurring_task_id,
            "project_id": task_data['project_id'],
            "title": task_data['title'],
            "description": task_data['description'],
            "assigned_to_id": task_data['assigned_to_id'],
            "due_date": current_date.date().isoformat(),
            "status": "todo",
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        # Calculate next occurrence
        if task_data['recurrence_type'] == 'daily':
            current_date += timedelta(days=task_data['recurrence_interval'])
        elif task_data['recurrence_type'] == 'weekly':
            current_date += timedelta(weeks=task_data['recurrence_interval'])
        elif task_data['recurrence_type'] == 'monthly':
            current_date += timedelta(days=30 * task_data['recurrence_interval'])
        
        instances_created += 1

# ============================================
# PROJECT TEMPLATES
# ============================================

class ProjectTemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    tasks: List[Dict]
    settings: Optional[Dict] = {}

@router.post("/templates/project")
async def create_project_template(
    template: ProjectTemplateCreate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create project template"""
    try:
        template_id = str(uuid.uuid4())
        
        await db.table('project_templates').insert({
            "id": template_id,
            "organization_id": current_user['organization_id'],
            "name": template.name,
            "description": template.description,
            "tasks": template.tasks,
            "settings": template.settings,
            "created_by_id": current_user['id'],
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        return {
            "success": True,
            "template_id": template_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/templates/project/{template_id}/use")
async def use_project_template(
    template_id: str,
    project_name: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create project from template"""
    try:
        # Get template
        template = await db.table('project_templates').select('*')\
            .eq('id', template_id).single().execute()
        
        if not template.data:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Create project
        project_id = str(uuid.uuid4())
        await db.table('projects').insert({
            "id": project_id,
            "organization_id": current_user['organization_id'],
            "name": project_name,
            "description": template.data['description'],
            "status": "active",
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        # Create tasks from template
        for task_template in template.data['tasks']:
            await db.table('tasks').insert({
                "id": str(uuid.uuid4()),
                "project_id": project_id,
                "title": task_template['title'],
                "description": task_template.get('description'),
                "estimated_hours": task_template.get('estimated_hours'),
                "priority": task_template.get('priority', 'medium'),
                "status": "todo",
                "created_at": datetime.utcnow().isoformat()
            }).execute()
        
        return {
            "success": True,
            "project_id": project_id,
            "message": "Project created from template"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# SHIFT MANAGEMENT
# ============================================

class ShiftCreate(BaseModel):
    name: str
    start_time: str  # HH:MM format
    end_time: str
    days: List[int]  # 0=Monday, 6=Sunday
    color: Optional[str] = "#3B82F6"

class ShiftAssignment(BaseModel):
    shift_id: str
    user_id: str
    start_date: datetime
    end_date: Optional[datetime] = None

@router.post("/shifts")
async def create_shift(
    shift: ShiftCreate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create shift template"""
    try:
        shift_id = str(uuid.uuid4())
        
        await db.table('shifts').insert({
            "id": shift_id,
            "organization_id": current_user['organization_id'],
            "name": shift.name,
            "start_time": shift.start_time,
            "end_time": shift.end_time,
            "days": shift.days,
            "color": shift.color,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        return {
            "success": True,
            "shift_id": shift_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/shifts/assign")
async def assign_shift(
    assignment: ShiftAssignment,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Assign shift to user"""
    try:
        assignment_id = str(uuid.uuid4())
        
        await db.table('shift_assignments').insert({
            "id": assignment_id,
            "shift_id": assignment.shift_id,
            "user_id": assignment.user_id,
            "start_date": assignment.start_date.isoformat(),
            "end_date": assignment.end_date.isoformat() if assignment.end_date else None,
            "is_active": True,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        return {
            "success": True,
            "assignment_id": assignment_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/shifts/schedule/{user_id}")
async def get_user_schedule(
    user_id: str,
    start_date: datetime,
    end_date: datetime,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get user's shift schedule"""
    try:
        assignments = await db.table('shift_assignments').select('*, shifts(*)')\
            .eq('user_id', user_id)\
            .gte('start_date', start_date.isoformat())\
            .lte('start_date', end_date.isoformat())\
            .execute()
        
        return {
            "success": True,
            "schedule": assignments.data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# TWO-FACTOR AUTHENTICATION
# ============================================

@router.post("/2fa/enable")
async def enable_2fa(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Enable two-factor authentication"""
    try:
        # Generate secret
        secret = pyotp.random_base32()
        
        # Generate QR code
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=current_user['email'],
            issuer_name='WorkingTracker'
        )
        
        # Create QR code image
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        # Save secret (encrypted in production)
        await db.table('users').update({
            "totp_secret": secret,
            "totp_enabled": False,  # Enable after verification
            "updated_at": datetime.utcnow().isoformat()
        }).eq('id', current_user['id']).execute()
        
        return {
            "success": True,
            "secret": secret,
            "qr_code": f"data:image/png;base64,{img_str}",
            "message": "Scan QR code with authenticator app"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/2fa/verify")
async def verify_2fa(
    code: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Verify and enable 2FA"""
    try:
        # Get user's secret
        user = await db.table('users').select('*')\
            .eq('id', current_user['id']).single().execute()
        
        if not user.data or not user.data.get('totp_secret'):
            raise HTTPException(status_code=400, detail="2FA not initialized")
        
        # Verify code
        totp = pyotp.TOTP(user.data['totp_secret'])
        if not totp.verify(code):
            raise HTTPException(status_code=400, detail="Invalid code")
        
        # Enable 2FA
        await db.table('users').update({
            "totp_enabled": True,
            "updated_at": datetime.utcnow().isoformat()
        }).eq('id', current_user['id']).execute()
        
        return {
            "success": True,
            "message": "Two-factor authentication enabled"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/2fa/disable")
async def disable_2fa(
    password: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Disable two-factor authentication"""
    try:
        # Verify password (implementation needed)
        # ... password verification logic ...
        
        # Disable 2FA
        await db.table('users').update({
            "totp_enabled": False,
            "totp_secret": None,
            "updated_at": datetime.utcnow().isoformat()
        }).eq('id', current_user['id']).execute()
        
        return {
            "success": True,
            "message": "Two-factor authentication disabled"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# HELPER FUNCTIONS
# ============================================

async def get_current_user():
    """Get current user"""
    pass

async def get_db():
    """Get database connection"""
    pass
