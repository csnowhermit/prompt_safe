from pydantic import BaseModel, Field
from typing import Optional, List


class Message(BaseModel):
    role: str = Field(description="角色: system/user/assistant")
    content: str = Field(description="消息内容")


class ChatRequest(BaseModel):
    session_id: Optional[str] = Field(default=None, description="会话ID")
    user_id: str = Field(description="用户ID")
    role: str = Field(default="end_user", description="用户角色")
    message: str = Field(description="用户消息")
    context: Optional[dict] = Field(default=None, description="上下文")
    mode: str = Field(default="chat", description="模式: chat/rag/agent/code")


class ChatResponse(BaseModel):
    session_id: str = Field(description="会话ID")
    response: str = Field(description="响应内容")
    risk_level: str = Field(description="风险等级")
    safety_actions: List[str] = Field(description="安全处理动作")
    latency_ms: float = Field(description="延迟(毫秒)")