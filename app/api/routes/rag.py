from fastapi import APIRouter, HTTPException

from app.services.rag_guard import RAGGuardService

router = APIRouter()

rag_guard = RAGGuardService()


@router.post("/ingest")
async def ingest_document(document: dict):
    result = await rag_guard.ingest_document(document, {"user_id": "", "role": "end_user"})
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["reason"])
    return result


@router.post("/filter")
async def filter_results(raw_results: list):
    filtered = await rag_guard.filter_retrieval_results(raw_results, {"user_id": "", "role": "end_user"})
    return {"results": filtered, "count": len(filtered)}