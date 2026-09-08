"""用户相关 Pydantic 模型。"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str
    password: str = Field(..., min_length=6, max_length=128)
    nickname: Optional[str] = Field(None, max_length=50)


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserProfileUpdate(BaseModel):
    nickname: Optional[str] = Field(None, max_length=50)
    bio: Optional[str] = Field(None, max_length=500)
    avatar: Optional[str] = Field(None, max_length=255)


class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    nickname: str
    avatar: str
    bio: str
    status: int
    created_at: datetime

    model_config = {"from_attributes": True}
