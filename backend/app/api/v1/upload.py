"""文件上传路由（§5.9）。"""
from fastapi import APIRouter, Depends, File, UploadFile

from app.api.deps import get_current_user_id
from app.config import settings
from app.core.exceptions import APIException
from app.core.response import success
from app.utils.file_handler import save_upload, validate_image

router = APIRouter(prefix="/upload", tags=["上传"])


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...), user_id: int = Depends(get_current_user_id)
):
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise APIException(400, "文件过大")
    validate_image(file.filename or "", file.content_type or "")
    url = await save_upload(content, file.filename or "")
    return success({"url": url})
