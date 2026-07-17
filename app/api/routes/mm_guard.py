from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_current_user
from app.services.mm_guard import MMGuardService

router = APIRouter()

mm_guard = MMGuardService()


@router.post("/process")
async def process_multimodal(input_data: dict, current_user: dict = Depends(get_current_user)):
    try:
        result = await mm_guard.process_multimodal_input(
            input_data,
            {"user_id": current_user.get("sub"), "role": current_user.get("role")}
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))