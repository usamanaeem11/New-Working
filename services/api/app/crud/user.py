"""
User CRUD Operations
Real database operations for user management
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from passlib.context import CryptContext

from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    return pwd_context.verify(plain_password, hashed_password)

def get_user(db: Session, user_id: int, tenant_id: int) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(
        and_(
            User.id == user_id,
            User.tenant_id == tenant_id
        )
    ).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()

def get_users(
    db: Session,
    tenant_id: int,
    skip: int = 0,
    limit: int = 100,
    role: Optional[str] = None,
    is_active: Optional[bool] = None
) -> List[User]:
    """Get all users with filters"""
    query = db.query(User).filter(User.tenant_id == tenant_id)
    
    if role:
        query = query.filter(User.role == role)
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    return query.offset(skip).limit(limit).all()

def create_user(db: Session, user_data: dict, tenant_id: int) -> User:
    """Create new user"""
    # Hash password
    hashed_password = get_password_hash(user_data.pop('password'))
    
    user = User(
        tenant_id=tenant_id,
        password_hash=hashed_password,
        **user_data
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_user(
    db: Session,
    user_id: int,
    tenant_id: int,
    user_data: dict
) -> Optional[User]:
    """Update user"""
    user = get_user(db, user_id, tenant_id)
    
    if not user:
        return None
    
    # Handle password change
    if 'password' in user_data:
        user_data['password_hash'] = get_password_hash(user_data.pop('password'))
    
    # Update fields
    for key, value in user_data.items():
        if hasattr(user, key) and value is not None:
            setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user_id: int, tenant_id: int) -> bool:
    """Deactivate user"""
    user = get_user(db, user_id, tenant_id)
    
    if not user:
        return False
    
    user.is_active = False
    db.commit()
    return True
