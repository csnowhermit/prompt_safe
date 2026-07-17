from pydantic import BaseModel, Field
from typing import Optional, List, Dict


class ParamDefinition(BaseModel):
    name: str = Field(description="参数名")
    type: str = Field(description="参数类型")
    pattern: Optional[str] = Field(default=None, description="正则模式")
    max_length: Optional[int] = Field(default=None, description="最大长度")
    min: Optional[float] = Field(default=None, description="最小值")
    max: Optional[float] = Field(default=None, description="最大值")


class ToolDefinition(BaseModel):
    name: str = Field(description="工具名称")
    auth_level: str = Field(description="鉴权级别: public/employee/restricted/admin")
    params: List[ParamDefinition] = Field(description="参数定义")
    rate_limit: Optional[Dict] = Field(default=None, description="速率限制")
    requires_approval: bool = Field(default=False, description="是否需要审批")


class ToolExecutionRequest(BaseModel):
    tool_name: str = Field(description="工具名称")
    params: Dict = Field(description="工具参数")
    user_id: str = Field(description="用户ID")
    role: str = Field(default="end_user", description="用户角色")


class ToolExecutionResponse(BaseModel):
    success: bool = Field(description="执行是否成功")
    result: Optional[Dict] = Field(default=None, description="执行结果")
    error: Optional[str] = Field(default=None, description="错误信息")