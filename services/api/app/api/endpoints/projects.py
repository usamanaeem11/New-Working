from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_all():
    return {"data": [], "total": 0}

@router.post("/")
async def create(data: dict):
    return {"id": "1", **data}

@router.get("/{item_id}")
async def get_one(item_id: str):
    return {"id": item_id}

@router.put("/{item_id}")
async def update(item_id: str, data: dict):
    return {"id": item_id, **data}

@router.delete("/{item_id}")
async def delete(item_id: str):
    return {"message": "Deleted successfully"}
