"""认证路由（§5.2）。"""
from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials

from app.api.deps import get_current_user_id, security
from app.core.response import success
from app.core.security import decode_token
from app.schemas.user import UserLogin, UserOut, UserRegister
from app.services import auth_service, user_service

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register")
async def register(data: UserRegister):
    user = await auth_service.register(data)
    return success(UserOut.model_validate(user).model_dump())


@router.post("/login")
async def login(data: UserLogin):
    result = await auth_service.login(data)
    return success(result)


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_id: int = Depends(get_current_user_id),
):
    jti = ""
    if credentials is not None:
        try:
            payload = decode_token(credentials.credentials)
            jti = payload.get("jti", "")
        except Exception:
            jti = ""
    await auth_service.logout(user_id, jti)
    return success()


@router.post("/refresh")
async def refresh(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_id: int = Depends(get_current_user_id),
):
    # 骨架：刷新 Token 逻辑与登录签发保持一致（此处返回当前用户信息占位）
    user = await user_service.get_user(user_id)
    return success(UserOut.model_validate(user).model_dump())


@router.get("/me")
async def me(user_id: int = Depends(get_current_user_id)):
    user = await user_service.get_user(user_id)
    return success(UserOut.model_validate(user).model_dump())
