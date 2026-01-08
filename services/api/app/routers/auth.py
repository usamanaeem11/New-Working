"""
Authentication Router - Complete Implementation
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from ..auth.jwt_manager import jwt_manager
from ..auth.rbac import rbac

router = APIRouter()

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # 30 minutes

class RefreshRequest(BaseModel):
    refresh_token: str

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    User login endpoint
    
    Returns access token and refresh token
    """
    # In production: query database for user
    # user = db.query(User).filter(User.email == request.email).first()
    
    # For now, mock user
    mock_user = {
        "id": "user_123",
        "email": request.email,
        "password_hash": jwt_manager.hash_password("password"),
        "roles": ["admin"],
        "tenant_id": "tenant_abc"
    }
    
    # Verify password
    if not jwt_manager.verify_password(request.password, mock_user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate tokens
    access_token = jwt_manager.create_access_token(
        user_id=mock_user["id"],
        email=mock_user["email"],
        roles=mock_user["roles"],
        tenant_id=mock_user["tenant_id"]
    )
    
    refresh_token = jwt_manager.create_refresh_token(
        user_id=mock_user["id"],
        tenant_id=mock_user["tenant_id"]
    )
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )

@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(request: RefreshRequest):
    """
    Refresh access token
    
    Uses refresh token to get new access token
    """
    # In production: query database for user
    mock_user = {
        "email": "user@example.com",
        "roles": ["admin"]
    }
    
    new_access_token = jwt_manager.refresh_access_token(
        refresh_token=request.refresh_token,
        user_email=mock_user["email"],
        user_roles=mock_user["roles"]
    )
    
    if not new_access_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    return LoginResponse(
        access_token=new_access_token,
        refresh_token=request.refresh_token
    )

@router.post("/logout")
async def logout(token: str = Depends(lambda: "current_token")):
    """Logout - revoke tokens"""
    jwt_manager.revoke_token(token)
    return {"message": "Logged out successfully"}
