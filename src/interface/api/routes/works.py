from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from src.app.services.work_service import WorkService
from src.entities.dto.works import (
    CreateWorkUploadRequest,
    ModerateWorkDeletionRequest,
    UpdateWorkRequest,
    WorkFeedResponse,
    WorkResponse,
    WorkSearchFeedResponse,
    WorkTypeResponse,
    WorkUploadResponse,
)
from src.entities.exceptions.works import (
    StorageDeleteError,
    StorageUploadError,
    UnsupportedWorkFileError,
    WorkNotFoundError,
    WorkSearchUnavailableError,
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
    owner_user_id: UUID | None = None,
) -> WorkFeedResponse:
    return await service.feed(viewer, limit, before, type_code, owner_user_id)


@router.get("/search", response_model=WorkSearchFeedResponse)
async def search(
    service: Annotated[WorkService, Depends(get_work_service)],
    viewer: Annotated[UUID | None, Depends(get_optional_user)],
    query: str = Query(min_length=2, max_length=500),
    limit: int = Query(20, ge=1, le=50),
    type_code: str | None = Query(default=None, min_length=1, max_length=64),
    cursor: int = Query(0, ge=0, le=10_000),
    owner_user_id: UUID | None = None,
) -> WorkSearchFeedResponse:
    try:
        return await service.search(
            query, viewer, limit, type_code, cursor, owner_user_id
        )
    except WorkSearchUnavailableError as error:
        raise HTTPException(
            503, "Semantic artwork search is temporarily unavailable."
        ) from error


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


@router.get("/saves", response_model=WorkFeedResponse)
async def saved_works(
    service: Annotated[WorkService, Depends(get_work_service)],
    user: Annotated[UUID, Depends(require_permission("profile.read_own"))],
    limit: int = Query(50, ge=1, le=50),
    before: datetime | None = None,
) -> WorkFeedResponse:
    return await service.profile_feed(user, limit, before, saved=True)


@router.get("/users/{user_id}", response_model=WorkFeedResponse)
async def user_works(
    user_id: UUID,
    service: Annotated[WorkService, Depends(get_work_service)],
    viewer: Annotated[UUID | None, Depends(get_optional_user)],
    limit: int = Query(50, ge=1, le=50),
    before: datetime | None = None,
) -> WorkFeedResponse:
    return await service.public_profile_feed(user_id, viewer, limit, before)


@router.get("/{work_id}", response_model=WorkResponse)
async def get_work(
    work_id: UUID,
    service: Annotated[WorkService, Depends(get_work_service)],
    viewer: Annotated[UUID | None, Depends(get_optional_user)],
) -> WorkResponse:
    try:
        return await service.get_published(work_id, viewer)
    except WorkNotFoundError as error:
        raise HTTPException(404, "The requested work was not found.") from error


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
    except UnsupportedWorkFileError as e:
        raise HTTPException(
            422, "Invalid image or image exceeds the pixel limit."
        ) from e
    except StorageUploadError as e:
        raise HTTPException(
            503, "Image preparation is temporarily unavailable. Please retry."
        ) from e


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


@router.put("/{work_id}/save", status_code=204)
async def save(
    work_id: UUID,
    service: Annotated[WorkService, Depends(get_work_service)],
    user: Annotated[UUID, Depends(require_permission("works.save"))],
) -> None:
    try:
        await service.save(work_id, user, True)
    except WorkNotFoundError as e:
        raise HTTPException(404, "Work not found.") from e


@router.delete("/{work_id}/save", status_code=204)
async def unsave(
    work_id: UUID,
    service: Annotated[WorkService, Depends(get_work_service)],
    user: Annotated[UUID, Depends(require_permission("works.save"))],
) -> None:
    try:
        await service.save(work_id, user, False)
    except WorkNotFoundError as e:
        raise HTTPException(404, "Work not found.") from e


@router.patch("/{work_id}", status_code=204)
async def update_work(
    work_id: UUID,
    request: UpdateWorkRequest,
    service: Annotated[WorkService, Depends(get_work_service)],
    user: Annotated[UUID, Depends(require_permission("works.upload"))],
) -> None:
    try:
        await service.update(work_id, user, request)
    except WorkTypeNotFoundError as error:
        raise HTTPException(422, "The selected work type is unavailable.") from error
    except WorkNotFoundError as error:
        raise HTTPException(404, "Work not found.") from error


@router.delete("/{work_id}", status_code=204)
async def delete_work(
    work_id: UUID,
    service: Annotated[WorkService, Depends(get_work_service)],
    user: Annotated[UUID, Depends(require_permission("works.upload"))],
) -> None:
    try:
        await service.delete(work_id, user)
    except WorkNotFoundError as error:
        raise HTTPException(404, "Work not found.") from error
    except StorageDeleteError as error:
        raise HTTPException(
            503, "Artwork storage could not be deleted safely."
        ) from error


@router.delete("/{work_id}/moderation", status_code=204)
async def delete_work_as_moderator(
    work_id: UUID,
    request: ModerateWorkDeletionRequest,
    service: Annotated[WorkService, Depends(get_work_service)],
    moderator: Annotated[UUID, Depends(require_permission("works.delete_any"))],
) -> None:
    try:
        await service.delete_as_moderator(work_id, moderator, request)
    except WorkNotFoundError as error:
        raise HTTPException(404, "Work not found.") from error
    except StorageDeleteError as error:
        raise HTTPException(
            503, "Artwork storage could not be deleted safely."
        ) from error
