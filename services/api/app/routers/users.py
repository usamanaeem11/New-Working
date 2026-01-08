"""
Users Router - REAL IMPLEMENTATION
Full user management with database
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

from app.database.session import get_db
from app.auth.jwt_manager import get_current_user
from app.auth.rbac import require_permission, Permission
from app.logging.logging_config import log_audit_event
from app.crud import user as user_crud

router = APIRouter()

# Pydantic Models
class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    role: str = 'employee'

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    tenant_id: int
    is_active: bool
    last_login: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[UserResponse])
@require_permission(Permission.USER_READ)
async def get_users(
    skip: int = 0,
    limit: int = 100,
    role: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all users - REAL DATABASE QUERY"""
    tenant_id = current_user['tenant_id']
    
    users = user_crud.get_users(db, tenant_id, skip, limit, role)
    return users

@router.get("/{user_id}", response_model=UserResponse)
@require_permission(Permission.USER_READ)
async def get_user(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get single user - REAL DATABASE QUERY"""
    tenant_id = current_user['tenant_id']
    
    user = user_crud.get_user(db, user_id, tenant_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@require_permission(Permission.USER_CREATE)
async def create_user(
    user: UserCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create user - REAL DATABASE INSERT"""
    tenant_id = current_user['tenant_id']
    
    # Check if email exists
    existing = user_crud.get_user_by_email(db, user.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    new_user = user_crud.create_user(db, user.dict(), tenant_id)
    
    log_audit_event(
        event_type='user_create',
        user_id=current_user['id'],
        tenant_id=tenant_id,
        resource='users',
        action='create',
        details={'new_user_id': new_user.id, 'email': user.email}
    )
    
    return new_user

@router.put("/{user_id}", response_model=UserResponse)
@require_permission(Permission.USER_UPDATE)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user - REAL DATABASE UPDATE"""
    tenant_id = current_user['tenant_id']
    
    updated_user = user_crud.update_user(
        db, user_id, tenant_id, user_update.dict(exclude_unset=True)
    )
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    log_audit_event(
        event_type='user_update',
        user_id=current_user['id'],
        tenant_id=tenant_id,
        resource='users',
        action='update',
        details={'updated_user_id': user_id}
    )
    
    return updated_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_permission(Permission.USER_DELETE)
async def delete_user(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete user (deactivate) - REAL DATABASE UPDATE"""
    tenant_id = current_user['tenant_id']
    
    success = user_crud.delete_user(db, user_id, tenant_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    log_audit_event(
        event_type='user_delete',
        user_id=current_user['id'],
        tenant_id=tenant_id,
        resource='users',
        action='delete',
        details={'deleted_user_id': user_id}
    )
    
    return None
