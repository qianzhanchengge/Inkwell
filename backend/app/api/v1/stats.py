"""统计路由（§5.8）。"""
from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user_id
from app.core.response import success
from app.services import stats_service

router = APIRouter(prefix="/stats", tags=["统计"])


@router.get("/overview")
async def overview(user_id: int = Depends(get_current_user_id)):
    return success(await stats_service.overview(user_id))


@router.get("/trend")
async def trend(
    days: int = Query(30, ge=1, le=365),
    user_id: int = Depends(get_current_user_id),
):
    return success(await stats_service.trend(user_id, days))
