from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional, List

from app.core.security_context import OutputDecision, RiskLevel


class OutputAction(BaseModel):
    action: str = Field(description="执行的动作")
    count: Optional[int] = Field(default=None, description="处理数量")


class OutputGuardRequest(BaseModel):
    trace_id: str = Field(description="追踪ID")
    raw_output: str = Field(description="模型原始输出")
    context: Optional[dict] = Field(default=None, description="上下文信息")


class OutputGuardResponse(BaseModel):
    trace_id: str = Field(description="追踪ID")
    decision: OutputDecision = Field(description="决策结果")
    final_output: str = Field(description="处理后输出")
    actions: List[OutputAction] = Field(description="执行的动作列表")
    block_reason: Optional[str] = Field(default=None, description="拦截原因")