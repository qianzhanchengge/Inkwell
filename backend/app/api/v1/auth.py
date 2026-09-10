"""认证路由（§５.2，工作台会话 scope=workbench）。"""
from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials

from app.api.deps import extract_jti, get_current_user_id, security
from app.core.response import success
from app.core.security import SCOPE_WORKBENCH
from app.schemas.user import RefreshRequest, UserLogin, UserOut, UserRegister
from app.services import auth_service, user_service

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register")
async def register(data: UserRegister):
    """工作台注册：创建 user_type=1 的工作台用户。"""
    user = await auth_service.register(data, user_type=auth_service.USER_TYPE_WORKBENCH)
    return success(UserOut.model_validate(user).model_dump())


@router.post("/login")
async def login(data: UserLogin):
    """工作台登录：仅工作台用户；博客用户返回 403。"""
    result = await auth_service.login(data, scope=SCOPE_WORKBENCH)
    return success(result)


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_id: int = Depends(get_current_user_id),
):
    token = credentials.credentials if credentials is not None else ""
    await auth_service.logout(
        user_id, extract_jti(credentials), token, scope=SCOPE_WORKBENCH
    )
    return success()


@router.post("/refresh")
async def refresh(data: RefreshRequest):
    result = await auth_service.refresh(
        data.refresh_token, expected_scope=SCOPE_WORKBENCH
    )
    return success(result)


@router.get("/me")
async def me(user_id: int = Depends(get_current_user_id)):
    user = await user_service.get_user(user_id)
    return success(UserOut.model_validate(user).model_dump())
