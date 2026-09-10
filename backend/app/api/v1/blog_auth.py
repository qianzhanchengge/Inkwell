"""博客认证路由（``/blog/auth``）：与工作台完全独立的博客会话。

- 注册：创建 ``user_type=2`` 的博客用户
- 登录：工作台用户（``user_type=1``）与博客用户（``user_type=2``）均可
- 签发 Token 的 ``scope=blog``，与工作台会话互不影响
"""
from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials

from app.api.deps import extract_jti, get_blog_user_id, security
from app.core.response import success
from app.core.security import SCOPE_BLOG
from app.schemas.user import RefreshRequest, UserLogin, UserOut, UserRegister
from app.services import auth_service, user_service

router = APIRouter(prefix="/blog/auth", tags=["博客认证"])


@router.post("/register")
async def register(data: UserRegister):
    """博客注册：创建博客用户（user_type=2）。"""
    user = await auth_service.register(data, user_type=auth_service.USER_TYPE_BLOG)
    return success(UserOut.model_validate(user).model_dump())


@router.post("/login")
async def login(data: UserLogin):
    """博客登录：工作台用户与博客用户均可登录。"""
    result = await auth_service.login(data, scope=SCOPE_BLOG)
    return success(result)


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_id: int = Depends(get_blog_user_id),
):
    token = credentials.credentials if credentials is not None else ""
    await auth_service.logout(
        user_id, extract_jti(credentials), token, scope=SCOPE_BLOG
    )
    return success()


@router.post("/refresh")
async def refresh(data: RefreshRequest):
    result = await auth_service.refresh(data.refresh_token, expected_scope=SCOPE_BLOG)
    return success(result)


@router.get("/me")
async def me(user_id: int = Depends(get_blog_user_id)):
    user = await user_service.get_user(user_id)
    return success(UserOut.model_validate(user).model_dump())
