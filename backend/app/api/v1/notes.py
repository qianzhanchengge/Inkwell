"""笔记路由（§5.4）。"""
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user_id, get_pagination
from app.core.response import success
from app.schemas.note import NoteCreate, NoteUpdate
from app.services import note_service

router = APIRouter(prefix="/notes", tags=["笔记"])


@router.get("")
async def list_notes(
    category_id: Optional[int] = Query(None),
    keyword: Optional[str] = Query(None),
    pagination=Depends(get_pagination),
    user_id: int = Depends(get_current_user_id),
):
    page, page_size = pagination
    result = await note_service.list_notes(user_id, page, page_size, category_id, keyword)
    return success(result)


@router.get("/search")
async def search_notes(
    keyword: str = Query(..., min_length=1),
    pagination=Depends(get_pagination),
    user_id: int = Depends(get_current_user_id),
):
    page, page_size = pagination
    result = await note_service.search_notes(user_id, keyword, page, page_size)
    return success(result)


@router.get("/{note_id}")
async def get_note(note_id: int, user_id: int = Depends(get_current_user_id)):
    return success(await note_service.get_note(user_id, note_id))


@router.post("")
async def create_note(data: NoteCreate, user_id: int = Depends(get_current_user_id)):
    return success(await note_service.create_note(user_id, data))


@router.put("/{note_id}")
async def update_note(
    note_id: int, data: NoteUpdate, user_id: int = Depends(get_current_user_id)
):
    return success(await note_service.update_note(user_id, note_id, data))


@router.delete("/{note_id}")
async def delete_note(note_id: int, user_id: int = Depends(get_current_user_id)):
    await note_service.delete_note(user_id, note_id)
    return success()


@router.patch("/{note_id}/pin")
async def toggle_pin(note_id: int, user_id: int = Depends(get_current_user_id)):
    pinned = await note_service.toggle_pin(user_id, note_id)
    return success({"is_pinned": pinned})
