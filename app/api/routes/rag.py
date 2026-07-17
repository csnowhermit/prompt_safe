from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_current_user
from app.services.rag_guard import RAGGuardService

router = APIRouter()

rag_guard = RAGGuardService()


@router.post("/ingest")
async def ingest_document(document: dict, current_user: dict = Depends(get_current_user)):
    result = await rag_guard.ingest_document(document, {"user_id": current_user.get("sub"), "role": current_user.get("role")})
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["reason"])
    return result


@router.post("/filter")
async def filter_results(raw_results: list, current_user: dict = Depends(get_current_user)):
    filtered = await rag_guard.filter_retrieval_results(raw_results, {"user_id": current_user.get("sub"), "role": current_user.get("role")})
    return {"results": filtered, "count": len(filtered)}