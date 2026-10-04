from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from src.app.services.work_service import WorkService
from src.entities.dto.works import (
    CreateWorkUploadRequest,
    WorkFeedResponse,
    WorkTypeResponse,
    WorkUploadResponse,
)
from src.entities.exceptions.works import (
    StorageUploadError,
    UnsupportedWorkFileError,
    WorkNotFoundError,
    WorkTypeNotFoundError,
)
from src.interface.dependencies.authentication import (
    get_optional_user,
    require_permission,
)
from src.interface.dependencies.works import get_work_service

router = APIRouter(prefix="/works", tags=["works"])


@router.get("/types", response_model=list[WorkTypeResponse])
async def list_types(
    service: Annotated[WorkService, Depends(get_work_service)],
) -> list[WorkTypeResponse]:
    return await service.list_types()


@router.get("", response_model=WorkFeedResponse)
async def feed(
    service: Annotated[WorkService, Depends(get_work_service)],
    viewer: Annotated[UUID | None, Depends(get_optional_user)],
    limit: int = Query(20, ge=1, le=50),
    before: datetime | None = None,
    type_code: str | None = Query(default=None, min_length=1, max_length=64),
) -> WorkFeedResponse:
    return await service.feed(viewer, limit, before, type_code)


@router.get("/me", response_model=WorkFeedResponse)
async def my_works(
    service: Annotated[WorkService, Depends(get_work_service)],
    user: Annotated[UUID, Depends(require_permission("profile.read_own"))],
    limit: int = Query(50, ge=1, le=50),
    before: datetime | None = None,
) -> WorkFeedResponse:
    return await service.profile_feed(user, limit, before)


@router.get("/likes", response_model=WorkFeedResponse)
async def liked_works(
    service: Annotated[WorkService, Depends(get_work_service)],
    user: Annotated[UUID, Depends(require_permission("profile.read_own"))],
    limit: int = Query(50, ge=1, le=50),
    before: datetime | None = None,
) -> WorkFeedResponse:
    return await service.profile_feed(user, limit, before, liked=True)


@router.post("/uploads", response_model=WorkUploadResponse, status_code=201)
async def prepare_upload(
    request: CreateWorkUploadRequest,
    service: Annotated[WorkService, Depends(get_work_service)],
    user: Annotated[UUID, Depends(require_permission("works.upload"))],
) -> WorkUploadResponse:
    try:
        return await service.prepare_upload(user, request)
    except WorkTypeNotFoundError as e:
        raise HTTPException(422, "The selected work type is unavailable.") from e
    except UnsupportedWorkFileError as e:
        raise HTTPException(
            422, "Only JPEG, PNG, WebP, and GIF images are supported."
        ) from e
    except StorageUploadError as e:
        raise HTTPException(503, "Image storage is temporarily unavailable.") from e


@router.post("/{work_id}/publish", status_code=204)
async def publish(
    work_id: UUID,
    service: Annotated[WorkService, Depends(get_work_service)],
    user: Annotated[UUID, Depends(require_permission("works.upload"))],
) -> None:
    try:
        await service.publish(work_id, user)
    except WorkNotFoundError as e:
        raise HTTPException(404, "Work not found.") from e


@router.put("/{work_id}/like", status_code=204)
async def like(
    work_id: UUID,
    service: Annotated[WorkService, Depends(get_work_service)],
    user: Annotated[UUID, Depends(require_permission("works.like"))],
) -> None:
    try:
        await service.like(work_id, user, True)
    except WorkNotFoundError as e:
        raise HTTPException(404, "Work not found.") from e


@router.delete("/{work_id}/like", status_code=204)
async def unlike(
    work_id: UUID,
    service: Annotated[WorkService, Depends(get_work_service)],
    user: Annotated[UUID, Depends(require_permission("works.like"))],
) -> None:
    try:
        await service.like(work_id, user, False)
    except WorkNotFoundError as e:
        raise HTTPException(404, "Work not found.") from e
