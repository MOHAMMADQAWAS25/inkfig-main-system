from datetime import datetime
from typing import Protocol
from uuid import UUID

from src.entities.dto.works import (
    CreateWorkUploadRequest,
    WorkResponse,
    WorkTypeResponse,
)


class WorkRepository(Protocol):
    async def list_types(self) -> list[WorkTypeResponse]: ...
    async def create_draft(
        self,
        work_id: UUID,
        owner_id: UUID,
        data: CreateWorkUploadRequest,
        bucket: str,
        path: str,
    ) -> None: ...
    async def publish(self, work_id: UUID, owner_id: UUID) -> bool: ...
    async def draft_path(self, work_id: UUID, owner_id: UUID) -> str | None: ...
    async def list_published(
        self,
        viewer_id: UUID | None,
        limit: int,
        before: datetime | None,
        type_code: str | None,
        owner_id: UUID | None = None,
        liked_by_id: UUID | None = None,
    ) -> list[WorkResponse]: ...
    async def set_like(self, work_id: UUID, user_id: UUID, liked: bool) -> bool: ...


class WorkStorage(Protocol):
    async def create_signed_upload(self, path: str) -> tuple[str, str]: ...
    async def object_exists(self, path: str) -> bool: ...
