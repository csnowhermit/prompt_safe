from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional, List

from app.core.security_context import RiskLevel, DecisionType, IntentType


class MediaItem(BaseModel):
    type: str = Field(description="媒体类型: image/audio/video/file")
    url: str = Field(description="媒体URL")
    size: int = Field(description="文件大小(字节)")


class InputGuardRequest(BaseModel):
    trace_id: Optional[str] = Field(default=None, description="追踪ID")
    session_id: Optional[str] = Field(default=None, description="会话ID")
    user_id: str = Field(description="用户ID")
    role: str = Field(default="end_user", description="用户角色")
    text: str = Field(description="用户输入文本")
    media: Optional[List[MediaItem]] = Field(default=None, description="多模态输入")
    context: Optional[dict] = Field(default=None, description="场景上下文")


class RuleTriggered(BaseModel):
    rule_id: str = Field(description="规则ID")
    match: str = Field(description="匹配内容")
    category: str = Field(description="规则类别")


class Classification(BaseModel):
    intent: IntentType = Field(description="意图分类")
    confidence: float = Field(description="置信度")


class Metrics(BaseModel):
    char_count: int = Field(description="字符数")
    obfuscation_score: float = Field(description="混淆分数")
    processing_ms: float = Field(description="处理耗时(毫秒)")


class InputGuardResponse(BaseModel):
    trace_id: str = Field(description="追踪ID")
    risk_level: RiskLevel = Field(description="风险等级")
    decision: DecisionType = Field(description="决策结果")
    sanitized_text: str = Field(description="脱敏后的文本")
    rules_triggered: List[RuleTriggered] = Field(description="命中的规则")
    classification: Classification = Field(description="意图分类")
    metrics: Metrics = Field(description="处理指标")