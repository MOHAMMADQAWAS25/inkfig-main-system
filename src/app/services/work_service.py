import asyncio
from datetime import datetime
from typing import ClassVar
from uuid import UUID, uuid4

from src.entities.dto.works import (
    CreateWorkUploadRequest,
    WorkFeedResponse,
    WorkTypeResponse,
    WorkUploadResponse,
)
from src.entities.exceptions.works import (
    UnsupportedWorkFileError,
    WorkNotFoundError,
    WorkSearchUnavailableError,
)
from src.entities.repositories.works import (
    WorkEmbeddingProvider,
    WorkRepository,
    WorkStorage,
)


class WorkService:
    ALLOWED: ClassVar[dict[str, str]] = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
    }

    def __init__(
        self,
        repository: WorkRepository,
        storage: WorkStorage,
        bucket: str,
        embedding_provider: WorkEmbeddingProvider | None = None,
    ) -> None:
        self._repository, self._storage, self._bucket = repository, storage, bucket
        self._embedding_provider = embedding_provider

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
        if self._embedding_provider is not None:
            try:
                embedding = await self._embedding_provider.embed_image(
                    self._storage.public_url(path)
                )
                await self._repository.save_embedding(
                    work_id, embedding, self._embedding_provider.model_name
                )
            except Exception:
                # Artwork publication must not depend on an external AI provider.
                # Missing embeddings are safe to retry through the backfill workflow.
                return

    async def search(
        self,
        query: str,
        viewer_id: UUID | None,
        limit: int,
        type_code: str | None = None,
    ) -> WorkFeedResponse:
        normalized = " ".join(query.split())
        if self._embedding_provider is None:
            raise WorkSearchUnavailableError
        try:
            await self._backfill_missing_embeddings()
            embedding = await self._embedding_provider.embed_query(normalized)
        except Exception as error:
            raise WorkSearchUnavailableError from error
        items = await self._repository.search_published(
            viewer_id, embedding, limit, type_code
        )
        return WorkFeedResponse(items=items)

    async def _backfill_missing_embeddings(self) -> None:
        if self._embedding_provider is None:
            return
        provider = self._embedding_provider
        pending = await self._repository.list_unembedded_paths(5)

        async def embed(work_id: UUID, path: str) -> tuple[UUID, list[float]] | None:
            try:
                embedding = await provider.embed_image(
                    self._storage.public_url(path)
                )
                return work_id, embedding
            except Exception:
                # A failed item remains eligible for a later bounded retry.
                return None

        embedded = await asyncio.gather(
            *(embed(work_id, path) for work_id, path in pending)
        )
        for result in embedded:
            if result is not None:
                await self._repository.save_embedding(
                    result[0], result[1], provider.model_name
                )

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
        saved: bool = False,
    ) -> WorkFeedResponse:
        items = await self._repository.list_published(
            user_id,
            limit + 1,
            before,
            None,
            owner_id=None if liked or saved else user_id,
            liked_by_id=user_id if liked else None,
            saved_by_id=user_id if saved else None,
        )
        next_cursor = items[limit - 1].created_at if len(items) > limit else None
        return WorkFeedResponse(items=items[:limit], next_cursor=next_cursor)

    async def public_profile_feed(
        self,
        profile_user_id: UUID,
        viewer_id: UUID | None,
        limit: int,
        before: datetime | None,
    ) -> WorkFeedResponse:
        items = await self._repository.list_published(
            viewer_id,
            limit + 1,
            before,
            None,
            owner_id=profile_user_id,
        )
        next_cursor = items[limit - 1].created_at if len(items) > limit else None
        return WorkFeedResponse(items=items[:limit], next_cursor=next_cursor)

    async def like(self, work_id: UUID, user_id: UUID, liked: bool) -> None:
        if not await self._repository.set_like(work_id, user_id, liked):
            raise WorkNotFoundError

    async def save(self, work_id: UUID, user_id: UUID, saved: bool) -> None:
        if not await self._repository.set_save(work_id, user_id, saved):
            raise WorkNotFoundError
