from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class Token(BaseModel):
    access_token: str = Field(description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")


class TokenData(BaseModel):
    username: Optional[str] = Field(default=None)
    role: Optional[str] = Field(default=None)


class UserCreate(BaseModel):
    username: str = Field(description="用户名")
    email: EmailStr = Field(description="邮箱")
    password: str = Field(description="密码")


class UserResponse(BaseModel):
    id: int = Field(description="用户ID")
    username: str = Field(description="用户名")
    email: EmailStr = Field(description="邮箱")
    is_active: bool = Field(description="是否活跃")


class LoginRequest(BaseModel):
    username: str = Field(description="用户名")
    password: str = Field(description="密码")