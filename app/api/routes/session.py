from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_current_user, require_role
from app.schemas.session import SessionCreate, SessionResponse, SessionListResponse
from app.services.session_manager import SessionManagerService

router = APIRouter()

session_manager = SessionManagerService()


@router.post("", response_model=SessionResponse)
async def create_session(request: SessionCreate, current_user: dict = Depends(get_current_user)):
    session_id = await session_manager.create_session(request.user_id, request.role)
    session_data = await session_manager.get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=400, detail="创建会话失败")
    return session_data


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str, current_user: dict = Depends(get_current_user)):
    session_data = await session_manager.get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="会话不存在")
    return session_data


@router.delete("/{session_id}")
async def terminate_session(session_id: str, current_user: dict = Depends(get_current_user)):
    success = await session_manager.terminate_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="会话不存在")
    return {"message": "会话已终止"}


@router.get("/user/{user_id}", response_model=SessionListResponse)
async def get_user_sessions(user_id: str, current_user: dict = Depends(require_role("admin"))):
    sessions = await session_manager.get_user_sessions(user_id)
    return {"sessions": sessions, "total": len(sessions)}