"""用户路由（§5.3）。"""
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.security import HTTPAuthorizationCredentials

from app.api.deps import extract_jti, get_current_user_id, security
from app.config import settings
from app.core.exceptions import APIException
from app.core.response import success
from app.schemas.user import PasswordUpdate, UserOut, UserProfileUpdate
from app.services import user_service
from app.utils.file_handler import save_upload, validate_image

router = APIRouter(prefix="/users", tags=["用户"])


@router.put("/profile")
async def update_profile(data: UserProfileUpdate, user_id: int = Depends(get_current_user_id)):
    user = await user_service.update_profile(user_id, data)
    return success(UserOut.model_validate(user).model_dump())


@router.put("/password")
async def change_password(
    data: PasswordUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_id: int = Depends(get_current_user_id),
):
    token = credentials.credentials if credentials is not None else ""
    await user_service.change_password(user_id, data, extract_jti(credentials), token)
    return success()


@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...), user_id: int = Depends(get_current_user_id)
):
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise APIException(400, "文件过大")
    validate_image(file.filename or "", file.content_type or "")
    url = await save_upload(content, file.filename or "")
    user = await user_service.update_profile(user_id, UserProfileUpdate(avatar=url))
    return success({"url": url})
