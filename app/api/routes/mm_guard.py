from fastapi import APIRouter, HTTPException

from app.services.mm_guard import MMGuardService

router = APIRouter()

mm_guard = MMGuardService()


@router.post("/process")
async def process_multimodal(input_data: dict):
    try:
        result = await mm_guard.process_multimodal_input(
            input_data,
            {"user_id": "anonymous", "role": "end_user"}
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))