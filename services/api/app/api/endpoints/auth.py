from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
async def login(request: LoginRequest):
    return {"access_token": "token", "token_type": "bearer"}

@router.post("/register")
async def register(request: LoginRequest):
    return {"message": "User registered successfully"}

@router.post("/logout")
async def logout():
    return {"message": "Logged out successfully"}
