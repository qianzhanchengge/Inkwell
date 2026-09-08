"""认证路由（§5.2）。"""
from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials

from app.api.deps import extract_jti, get_current_user_id, security
from app.core.response import success
from app.schemas.user import RefreshRequest, UserLogin, UserOut, UserRegister
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
    token = credentials.credentials if credentials is not None else ""
    await auth_service.logout(user_id, extract_jti(credentials), token)
    return success()


@router.post("/refresh")
async def refresh(data: RefreshRequest):
    result = await auth_service.refresh(data.refresh_token)
    return success(result)


@router.get("/me")
async def me(user_id: int = Depends(get_current_user_id)):
    user = await user_service.get_user(user_id)
    return success(UserOut.model_validate(user).model_dump())
