from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response

from src.app.services.feed_cursor import InvalidFeedCursorError
from src.app.services.work_service import WorkService
from src.entities.dto.feed import InfiniteFeedResponse
from src.interface.dependencies.authentication import get_optional_user
from src.interface.dependencies.works import get_work_service

router = APIRouter(prefix="/feed", tags=["feed"])


@router.get("", response_model=InfiniteFeedResponse)
async def infinite_feed(
    response: Response,
    service: Annotated[WorkService, Depends(get_work_service)],
    viewer: Annotated[UUID | None, Depends(get_optional_user)],
    cursor: str | None = None,
    limit: int = Query(20, ge=1, le=50),
    type_code: str | None = Query(default=None, min_length=1, max_length=64),
    owner_user_id: UUID | None = None,
) -> InfiniteFeedResponse:
    # Personalized interaction state must never enter shared/CDN caches.
    response.headers["Cache-Control"] = "private, no-store"
    response.headers["Vary"] = "Cookie, Authorization"
    try:
        return await service.infinite_feed(
            viewer, limit, cursor, type_code, owner_user_id
        )
    except InvalidFeedCursorError as error:
        raise HTTPException(400, str(error)) from error
