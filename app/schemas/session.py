from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SessionCreate(BaseModel):
    user_id: str = Field(description="用户ID")
    role: str = Field(default="end_user", description="用户角色")


class SessionResponse(BaseModel):
    session_id: str = Field(description="会话ID")
    user_id: str = Field(description="用户ID")
    role: str = Field(description="角色")
    status: str = Field(description="状态: active/idle/expired/terminated")
    turn_count: int = Field(description="对话轮次")
    max_turns: int = Field(description="最大轮次")
    created_at: datetime = Field(description="创建时间")
    last_active_at: datetime = Field(description="最后活跃时间")


class SessionListResponse(BaseModel):
    sessions: List[SessionResponse] = Field(description="会话列表")
    total: int = Field(description="会话总数")