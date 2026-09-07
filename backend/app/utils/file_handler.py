"""文件上传处理：类型白名单校验与重命名存储（§12.2）。"""
import uuid
from pathlib import Path

from app.config import settings
from app.core.exceptions import APIException

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp", "bmp"}
ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/bmp",
}


def validate_image(filename: str, content_type: str) -> None:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise APIException(400, "不支持的文件类型")
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise APIException(400, "仅支持图片上传")


def generate_filename(original_filename: str) -> str:
    ext = original_filename.rsplit(".", 1)[-1].lower() if "." in original_filename else ""
    return f"{uuid.uuid4().hex}.{ext}"


async def save_upload(content: bytes, original_filename: str) -> str:
    """保存上传文件，返回可访问的相对路径。"""
    filename = generate_filename(original_filename)
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / filename
    file_path.write_bytes(content)
    return f"/uploads/{filename}"
