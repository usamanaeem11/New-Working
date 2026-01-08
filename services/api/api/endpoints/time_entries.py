from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_time_entries():
    return {"time_entries": [], "total": 0}
