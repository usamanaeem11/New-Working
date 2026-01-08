from fastapi import APIRouter, HTTPException
from typing import List

router = APIRouter()

@router.get("/")
async def get_employees():
    return {"employees": [], "total": 0}

@router.post("/")
async def create_employee(employee: dict):
    return {"id": "1", **employee}

@router.get("/{employee_id}")
async def get_employee(employee_id: str):
    return {"id": employee_id, "name": "John Doe"}
