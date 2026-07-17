from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class PromptTemplate(BaseModel):
    role: str = Field(description="角色")
    scenario: str = Field(description="场景")
    version: str = Field(description="版本号")
    content: str = Field(description="模板内容")


class PromptVersionResponse(BaseModel):
    id: int = Field(description="ID")
    role: str = Field(description="角色")
    scenario: str = Field(description="场景")
    version: str = Field(description="版本号")
    content: str = Field(description="内容")
    review_status: str = Field(description="审核状态")
    created_at: datetime = Field(description="创建时间")