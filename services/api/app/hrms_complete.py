"""
Complete HRMS (Human Resource Management System) Endpoints
Includes: Leave Management, Payroll, Expenses, Attendance
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict
from datetime import datetime, date, timedelta
from decimal import Decimal
import uuid

router = APIRouter(prefix="/api/hrms", tags=["HRMS"])

# ============================================
# PYDANTIC MODELS
# ============================================

class LeaveRequestCreate(BaseModel):
    leave_type: str = Field(..., description="Type: sick, vacation, personal, etc.")
    start_date: date
    end_date: date
    reason: str
    half_day: bool = False
    
    @validator('end_date')
    def end_after_start(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v

class LeaveRequestUpdate(BaseModel):
    status: str = Field(..., description="Status: approved, rejected, cancelled")
    review_notes: Optional[str] = None

class PayrollCreate(BaseModel):
    user_id: str
    period_start: date
    period_end: date
    regular_hours: float = 0
    overtime_hours: float = 0
    bonus: Decimal = Decimal('0')
    deductions: Dict = {}

class ExpenseCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category: str
    amount: Decimal
    currency: str = "USD"
    expense_date: date
    project_id: Optional[str] = None
    receipt_url: Optional[str] = None

class AttendanceRecord(BaseModel):
    clock_in: datetime
    clock_out: Optional[datetime] = None
    location: Optional[Dict] = None
    notes: Optional[str] = None

# ============================================
# LEAVE MANAGEMENT ENDPOINTS
# ============================================

@router.post("/leave-requests")
async def create_leave_request(
    leave_request: LeaveRequestCreate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Create a new leave request
    """
    try:
        # Calculate days count
        delta = leave_request.end_date - leave_request.start_date
        days_count = delta.days + 1
        if leave_request.half_day:
            days_count = 0.5
        
        # Check leave balance
        leave_balance = await db.get_leave_balance(
            current_user['id'], 
            leave_request.leave_type
        )
        
        if leave_balance < days_count:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient leave balance. Available: {leave_balance} days"
            )
        
        # Create leave request
        leave_id = str(uuid.uuid4())
        leave_data = {
            "id": leave_id,
            "user_id": current_user['id'],
            "organization_id": current_user['organization_id'],
            "leave_type": leave_request.leave_type,
            "start_date": leave_request.start_date.isoformat(),
            "end_date": leave_request.end_date.isoformat(),
            "days_count": days_count,
            "reason": leave_request.reason,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }
        
        await db.table('leave_requests').insert(leave_data).execute()
        
        # Send notification to manager
        await send_notification(
            user_id=current_user['manager_id'],
            title="New Leave Request",
            message=f"{current_user['full_name']} has requested {days_count} days of {leave_request.leave_type} leave",
            action_url=f"/hrms/leaves/{leave_id}"
        )
        
        return {
            "success": True,
            "leave_request_id": leave_id,
            "status": "pending",
            "days_count": days_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/leave-requests")
async def get_leave_requests(
    status: Optional[str] = Query(None, description="Filter by status"),
    user_id: Optional[str] = Query(None, description="Filter by user"),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get all leave requests (filtered)
    """
    try:
        query = db.table('leave_requests').select('*')
        
        # Filter by organization
        query = query.eq('organization_id', current_user['organization_id'])
        
        # Apply filters
        if status:
            query = query.eq('status', status)
        if user_id:
            query = query.eq('user_id', user_id)
        elif current_user['role'] == 'employee':
            # Employees can only see their own requests
            query = query.eq('user_id', current_user['id'])
        
        # Order by date
        query = query.order('created_at', desc=True)
        
        response = await query.execute()
        
        # Enrich with user data
        leave_requests = []
        for leave in response.data:
            user = await db.get_user(leave['user_id'])
            leave['user'] = {
                'id': user['id'],
                'full_name': user['full_name'],
                'email': user['email'],
                'avatar_url': user.get('avatar_url')
            }
            leave_requests.append(leave)
        
        return {
            "success": True,
            "leave_requests": leave_requests,
            "total": len(leave_requests)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/leave-requests/{leave_id}")
async def update_leave_request(
    leave_id: str,
    update: LeaveRequestUpdate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Approve/reject a leave request (managers only)
    """
    try:
        # Check if user is manager
        if current_user['role'] not in ['manager', 'admin', 'owner']:
            raise HTTPException(status_code=403, detail="Only managers can review leave requests")
        
        # Get leave request
        leave = await db.table('leave_requests').select('*').eq('id', leave_id).single().execute()
        if not leave.data:
            raise HTTPException(status_code=404, detail="Leave request not found")
        
        # Update leave request
        update_data = {
            "status": update.status,
            "reviewed_by_id": current_user['id'],
            "reviewed_at": datetime.utcnow().isoformat(),
            "review_notes": update.review_notes,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        await db.table('leave_requests').update(update_data).eq('id', leave_id).execute()
        
        # Update leave balance if approved
        if update.status == 'approved':
            await db.deduct_leave_balance(
                leave.data['user_id'],
                leave.data['leave_type'],
                leave.data['days_count']
            )
        
        # Send notification to employee
        await send_notification(
            user_id=leave.data['user_id'],
            title=f"Leave Request {update.status.capitalize()}",
            message=f"Your {leave.data['leave_type']} leave request has been {update.status}",
            action_url=f"/hrms/leaves/{leave_id}"
        )
        
        return {
            "success": True,
            "leave_request_id": leave_id,
            "status": update.status
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/leave-balance/{user_id}")
async def get_leave_balance(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get leave balance for a user
    """
    try:
        # Check permissions
        if current_user['id'] != user_id and current_user['role'] not in ['manager', 'admin', 'owner']:
            raise HTTPException(status_code=403, detail="Cannot view other user's leave balance")
        
        # Get leave balances
        balances = await db.get_all_leave_balances(user_id)
        
        return {
            "success": True,
            "user_id": user_id,
            "balances": balances
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# PAYROLL ENDPOINTS
# ============================================

@router.post("/payroll")
async def create_payroll(
    payroll: PayrollCreate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Create payroll record (admin/owner only)
    """
    try:
        # Check permissions
        if current_user['role'] not in ['admin', 'owner']:
            raise HTTPException(status_code=403, detail="Only admins can create payroll")
        
        # Get user data
        user = await db.get_user(payroll.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Calculate gross pay
        hourly_rate = user.get('hourly_rate', 0) or 0
        regular_pay = payroll.regular_hours * Decimal(str(hourly_rate))
        overtime_pay = payroll.overtime_hours * Decimal(str(hourly_rate)) * Decimal('1.5')
        gross_pay = regular_pay + overtime_pay + payroll.bonus
        
        # Calculate deductions
        total_deductions = sum(Decimal(str(v)) for v in payroll.deductions.values())
        net_pay = gross_pay - total_deductions
        
        # Create payroll record
        payroll_id = str(uuid.uuid4())
        payroll_data = {
            "id": payroll_id,
            "user_id": payroll.user_id,
            "organization_id": current_user['organization_id'],
            "period_start": payroll.period_start.isoformat(),
            "period_end": payroll.period_end.isoformat(),
            "pay_date": (payroll.period_end + timedelta(days=7)).isoformat(),
            "regular_hours": payroll.regular_hours,
            "overtime_hours": payroll.overtime_hours,
            "bonus": float(payroll.bonus),
            "gross_pay": float(gross_pay),
            "tax_deductions": payroll.deductions,
            "net_pay": float(net_pay),
            "status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }
        
        await db.table('payroll').insert(payroll_data).execute()
        
        # Send notification
        await send_notification(
            user_id=payroll.user_id,
            title="Payroll Generated",
            message=f"Your payroll for {payroll.period_start} to {payroll.period_end} is ready",
            action_url=f"/hrms/payroll/{payroll_id}"
        )
        
        return {
            "success": True,
            "payroll_id": payroll_id,
            "gross_pay": float(gross_pay),
            "net_pay": float(net_pay)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/payroll")
async def get_payroll_records(
    user_id: Optional[str] = Query(None),
    period_start: Optional[date] = Query(None),
    period_end: Optional[date] = Query(None),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get payroll records (filtered)
    """
    try:
        query = db.table('payroll').select('*')
        
        # Filter by organization
        query = query.eq('organization_id', current_user['organization_id'])
        
        # Apply filters
        if user_id:
            query = query.eq('user_id', user_id)
        elif current_user['role'] == 'employee':
            query = query.eq('user_id', current_user['id'])
        
        if period_start:
            query = query.gte('period_start', period_start.isoformat())
        if period_end:
            query = query.lte('period_end', period_end.isoformat())
        
        query = query.order('period_start', desc=True)
        
        response = await query.execute()
        
        return {
            "success": True,
            "payroll_records": response.data,
            "total": len(response.data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/payroll/{payroll_id}/process")
async def process_payroll(
    payroll_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Process payroll payment (admin only)
    """
    try:
        # Check permissions
        if current_user['role'] not in ['admin', 'owner']:
            raise HTTPException(status_code=403, detail="Only admins can process payroll")
        
        # Update payroll status
        update_data = {
            "status": "processed",
            "processed_at": datetime.utcnow().isoformat(),
            "payment_reference": f"PAY-{payroll_id[:8].upper()}"
        }
        
        await db.table('payroll').update(update_data).eq('id', payroll_id).execute()
        
        return {
            "success": True,
            "payroll_id": payroll_id,
            "status": "processed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# EXPENSE MANAGEMENT ENDPOINTS
# ============================================

@router.post("/expenses")
async def create_expense(
    expense: ExpenseCreate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Submit a new expense
    """
    try:
        expense_id = str(uuid.uuid4())
        expense_data = {
            "id": expense_id,
            "user_id": current_user['id'],
            "organization_id": current_user['organization_id'],
            "project_id": expense.project_id,
            "title": expense.title,
            "description": expense.description,
            "category": expense.category,
            "amount": float(expense.amount),
            "currency": expense.currency,
            "expense_date": expense.expense_date.isoformat(),
            "receipt_url": expense.receipt_url,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }
        
        await db.table('expenses').insert(expense_data).execute()
        
        # Notify manager
        await send_notification(
            user_id=current_user.get('manager_id'),
            title="New Expense Submitted",
            message=f"{current_user['full_name']} submitted expense: {expense.title} - {expense.currency} {expense.amount}",
            action_url=f"/hrms/expenses/{expense_id}"
        )
        
        return {
            "success": True,
            "expense_id": expense_id,
            "status": "pending"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/expenses")
async def get_expenses(
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get expenses (filtered)
    """
    try:
        query = db.table('expenses').select('*')
        
        # Filter by organization
        query = query.eq('organization_id', current_user['organization_id'])
        
        # Apply filters
        if status:
            query = query.eq('status', status)
        if category:
            query = query.eq('category', category)
        if user_id:
            query = query.eq('user_id', user_id)
        elif current_user['role'] == 'employee':
            query = query.eq('user_id', current_user['id'])
        
        query = query.order('expense_date', desc=True)
        
        response = await query.execute()
        
        return {
            "success": True,
            "expenses": response.data,
            "total": len(response.data),
            "total_amount": sum(e['amount'] for e in response.data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/expenses/{expense_id}/approve")
async def approve_expense(
    expense_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Approve an expense (managers only)
    """
    try:
        # Check permissions
        if current_user['role'] not in ['manager', 'admin', 'owner']:
            raise HTTPException(status_code=403, detail="Only managers can approve expenses")
        
        # Get expense
        expense = await db.table('expenses').select('*').eq('id', expense_id).single().execute()
        if not expense.data:
            raise HTTPException(status_code=404, detail="Expense not found")
        
        # Update expense
        update_data = {
            "status": "approved",
            "approved_by_id": current_user['id'],
            "approved_at": datetime.utcnow().isoformat()
        }
        
        await db.table('expenses').update(update_data).eq('id', expense_id).execute()
        
        # Notify employee
        await send_notification(
            user_id=expense.data['user_id'],
            title="Expense Approved",
            message=f"Your expense '{expense.data['title']}' has been approved",
            action_url=f"/hrms/expenses/{expense_id}"
        )
        
        return {
            "success": True,
            "expense_id": expense_id,
            "status": "approved"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# ATTENDANCE ENDPOINTS
# ============================================

@router.post("/attendance/clock-in")
async def clock_in(
    attendance: AttendanceRecord,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Clock in for the day
    """
    try:
        # Check if already clocked in
        today = date.today()
        existing = await db.table('time_entries').select('*')\
            .eq('user_id', current_user['id'])\
            .gte('start_time', today.isoformat())\
            .is_('end_time', 'null')\
            .execute()
        
        if existing.data:
            raise HTTPException(status_code=400, detail="Already clocked in")
        
        # Create time entry
        entry_id = str(uuid.uuid4())
        entry_data = {
            "id": entry_id,
            "user_id": current_user['id'],
            "organization_id": current_user['organization_id'],
            "start_time": attendance.clock_in.isoformat(),
            "location": attendance.location,
            "description": attendance.notes or "Clock in",
            "source": "manual",
            "created_at": datetime.utcnow().isoformat()
        }
        
        await db.table('time_entries').insert(entry_data).execute()
        
        return {
            "success": True,
            "entry_id": entry_id,
            "clock_in": attendance.clock_in.isoformat(),
            "message": "Clocked in successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/attendance/clock-out")
async def clock_out(
    attendance: AttendanceRecord,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Clock out for the day
    """
    try:
        # Find active time entry
        today = date.today()
        active_entry = await db.table('time_entries').select('*')\
            .eq('user_id', current_user['id'])\
            .gte('start_time', today.isoformat())\
            .is_('end_time', 'null')\
            .single()\
            .execute()
        
        if not active_entry.data:
            raise HTTPException(status_code=400, detail="No active clock-in found")
        
        # Calculate duration
        start_time = datetime.fromisoformat(active_entry.data['start_time'])
        duration_seconds = int((attendance.clock_out - start_time).total_seconds())
        
        # Update time entry
        update_data = {
            "end_time": attendance.clock_out.isoformat(),
            "duration_seconds": duration_seconds,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        if attendance.notes:
            update_data["description"] = attendance.notes
        
        await db.table('time_entries').update(update_data)\
            .eq('id', active_entry.data['id']).execute()
        
        return {
            "success": True,
            "entry_id": active_entry.data['id'],
            "clock_out": attendance.clock_out.isoformat(),
            "duration_hours": round(duration_seconds / 3600, 2),
            "message": "Clocked out successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# HELPER FUNCTIONS
# ============================================

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Decode JWT and return current user"""
    # Implementation in main server.py
    pass

async def send_notification(user_id: str, title: str, message: str, action_url: str = None):
    """Send notification to user"""
    # Implementation in notifications.py
    pass

async def get_db():
    """Get database connection"""
    # Implementation in db.py
    pass
