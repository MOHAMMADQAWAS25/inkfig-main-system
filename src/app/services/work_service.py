from datetime import datetime
from typing import ClassVar
from uuid import UUID, uuid4

from src.entities.dto.works import (
    CreateWorkUploadRequest,
    WorkFeedResponse,
    WorkTypeResponse,
    WorkUploadResponse,
)
from src.entities.exceptions.works import UnsupportedWorkFileError, WorkNotFoundError
from src.entities.repositories.works import WorkRepository, WorkStorage


class WorkService:
    ALLOWED: ClassVar[dict[str, str]] = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
    }

    def __init__(
        self, repository: WorkRepository, storage: WorkStorage, bucket: str
    ) -> None:
        self._repository, self._storage, self._bucket = repository, storage, bucket

    async def list_types(self) -> list[WorkTypeResponse]:
        return await self._repository.list_types()

    async def prepare_upload(
        self, user_id: UUID, data: CreateWorkUploadRequest
    ) -> WorkUploadResponse:
        extension = self.ALLOWED.get(data.mime_type)
        if extension is None:
            raise UnsupportedWorkFileError
        work_id = uuid4()
        path = f"{user_id}/{work_id}{extension}"
        await self._repository.create_draft(work_id, user_id, data, self._bucket, path)
        upload_url, token = await self._storage.create_signed_upload(path)
        return WorkUploadResponse(
            work_id=work_id, object_path=path, upload_url=upload_url, upload_token=token
        )

    async def publish(self, work_id: UUID, user_id: UUID) -> None:
        path = await self._repository.draft_path(work_id, user_id)
        if path is None or not await self._storage.object_exists(path):
            raise WorkNotFoundError
        if not await self._repository.publish(work_id, user_id):
            raise WorkNotFoundError

    async def feed(
        self,
        viewer_id: UUID | None,
        limit: int,
        before: datetime | None,
        type_code: str | None = None,
    ) -> WorkFeedResponse:
        items = await self._repository.list_published(
            viewer_id, limit + 1, before, type_code
        )
        next_cursor = items[limit - 1].created_at if len(items) > limit else None
        return WorkFeedResponse(items=items[:limit], next_cursor=next_cursor)

    async def profile_feed(
        self,
        user_id: UUID,
        limit: int,
        before: datetime | None,
        liked: bool = False,
    ) -> WorkFeedResponse:
        items = await self._repository.list_published(
            user_id,
            limit + 1,
            before,
            None,
            owner_id=None if liked else user_id,
            liked_by_id=user_id if liked else None,
        )
        next_cursor = items[limit - 1].created_at if len(items) > limit else None
        return WorkFeedResponse(items=items[:limit], next_cursor=next_cursor)

    async def like(self, work_id: UUID, user_id: UUID, liked: bool) -> None:
        if not await self._repository.set_like(work_id, user_id, liked):
            raise WorkNotFoundError
