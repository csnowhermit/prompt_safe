from fastapi import APIRouter

from app.api.routes import chat, input_guard, output_guard, session, audit, rag, agent, mm_guard

api_router = APIRouter()
api_router.include_router(chat.router, prefix="/chat", tags=["聊天"])
api_router.include_router(input_guard.router, prefix="/guard/input", tags=["输入防护"])
api_router.include_router(output_guard.router, prefix="/guard/output", tags=["输出防护"])
api_router.include_router(session.router, prefix="/session", tags=["会话管理"])
api_router.include_router(audit.router, prefix="/audit", tags=["审计"])
api_router.include_router(rag.router, prefix="/rag", tags=["RAG安全"])
api_router.include_router(agent.router, prefix="/agent", tags=["Agent安全"])
api_router.include_router(mm_guard.router, prefix="/mm", tags=["多模态安全"])