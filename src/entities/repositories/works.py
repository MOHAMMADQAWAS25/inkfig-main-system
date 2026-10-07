from datetime import datetime
from typing import Protocol
from uuid import UUID

from src.entities.dto.works import (
    CreateWorkUploadRequest,
    ModeratedWorkTarget,
    UpdateWorkRequest,
    WorkResponse,
    WorkSearchResponse,
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
        saved_by_id: UUID | None = None,
    ) -> list[WorkResponse]: ...
    async def set_like(self, work_id: UUID, user_id: UUID, liked: bool) -> bool: ...
    async def set_save(self, work_id: UUID, user_id: UUID, saved: bool) -> bool: ...
    async def update_owned(
        self, work_id: UUID, owner_id: UUID, data: UpdateWorkRequest
    ) -> bool: ...
    async def owned_storage_path(self, work_id: UUID, owner_id: UUID) -> str | None: ...
    async def delete_owned(self, work_id: UUID, owner_id: UUID) -> bool: ...
    async def moderation_target(self, work_id: UUID) -> ModeratedWorkTarget | None: ...
    async def delete_moderated(
        self, target: ModeratedWorkTarget, moderator_id: UUID, reason: str
    ) -> bool: ...
    async def save_embedding(
        self, work_id: UUID, embedding: list[float], model_name: str
    ) -> None: ...
    async def search_published(
        self,
        viewer_id: UUID | None,
        embedding: list[float],
        limit: int,
        type_code: str | None,
        min_similarity: float,
        offset: int,
        owner_id: UUID | None = None,
    ) -> list[WorkSearchResponse]: ...
    async def list_unembedded_paths(self, limit: int) -> list[tuple[UUID, str]]: ...


class WorkStorage(Protocol):
    async def create_signed_upload(self, path: str) -> tuple[str, str]: ...
    async def object_exists(self, path: str) -> bool: ...
    async def delete_object(self, path: str) -> None: ...
    def public_url(self, path: str) -> str: ...


class WorkEmbeddingProvider(Protocol):
    model_name: str

    async def embed_query(self, query: str) -> list[float]: ...
    async def embed_image(self, image_url: str) -> list[float]: ...
