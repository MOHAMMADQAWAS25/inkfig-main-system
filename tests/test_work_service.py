from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest
from pydantic import HttpUrl, ValidationError

from src.app.services.work_service import WorkService
from src.entities.dto.works import (
    CreateWorkUploadRequest,
    ModeratedWorkTarget,
    ModerateWorkDeletionRequest,
    UpdateWorkRequest,
    WorkLinkRequest,
    WorkResponse,
    WorkSearchResponse,
    WorkTypeResponse,
)
from src.entities.exceptions.works import (
    UnsupportedWorkFileError,
    WorkNotFoundError,
    WorkSearchUnavailableError,
)


class FakeWorkRepository:
    def __init__(self) -> None:
        self.created: tuple[UUID, UUID, str] | None = None
        self.path: str | None = None
        self.published = False
        self.listed_type_code: str | None = None
        self.listed_viewer_id: UUID | None = None
        self.listed_owner_id: UUID | None = None
        self.listed_liked_by_id: UUID | None = None
        self.listed_saved_by_id: UUID | None = None
        self.saved: bool | None = None
        self.embedding: list[float] | None = None
        self.search_embedding: list[float] | None = None
        self.search_type_code: str | None = None
        self.search_min_similarity: float | None = None
        self.search_offset: int | None = None
        self.search_limit: int | None = None
        self.search_owner_id: UUID | None = None
        self.search_results: list[WorkSearchResponse] = []
        self.unembedded: list[tuple[UUID, str]] = []
        self.updated: UpdateWorkRequest | None = None
        self.owned_path: str | None = None
        self.deleted = False
        self.moderation: tuple[ModeratedWorkTarget, UUID, str] | None = None
        self.moderation_work: ModeratedWorkTarget | None = None

    async def list_types(self) -> list[WorkTypeResponse]:
        return []

    async def create_draft(
        self,
        work_id: UUID,
        owner_id: UUID,
        data: CreateWorkUploadRequest,
        bucket: str,
        path: str,
    ) -> None:
        del data, bucket
        self.created = (work_id, owner_id, path)
        self.path = path

    async def publish(self, work_id: UUID, owner_id: UUID) -> bool:
        del work_id, owner_id
        self.published = True
        return True

    async def draft_path(self, work_id: UUID, owner_id: UUID) -> str | None:
        del work_id, owner_id
        return self.path

    async def list_published(
        self,
        viewer_id: UUID | None,
        limit: int,
        before: datetime | None,
        type_code: str | None,
        owner_id: UUID | None = None,
        liked_by_id: UUID | None = None,
        saved_by_id: UUID | None = None,
    ) -> list[WorkResponse]:
        del limit, before
        self.listed_viewer_id = viewer_id
        self.listed_type_code = type_code
        self.listed_owner_id = owner_id
        self.listed_liked_by_id = liked_by_id
        self.listed_saved_by_id = saved_by_id
        return []

    async def set_like(self, work_id: UUID, user_id: UUID, liked: bool) -> bool:
        del work_id, user_id, liked
        return True

    async def set_save(self, work_id: UUID, user_id: UUID, saved: bool) -> bool:
        del work_id, user_id
        self.saved = saved
        return True

    async def update_owned(
        self, work_id: UUID, owner_id: UUID, data: UpdateWorkRequest
    ) -> bool:
        del work_id, owner_id
        self.updated = data
        return True

    async def owned_storage_path(self, work_id: UUID, owner_id: UUID) -> str | None:
        del work_id, owner_id
        return self.owned_path

    async def delete_owned(self, work_id: UUID, owner_id: UUID) -> bool:
        del work_id, owner_id
        self.deleted = True
        return True

    async def moderation_target(self, work_id: UUID) -> ModeratedWorkTarget | None:
        return (
            self.moderation_work
            if self.moderation_work and self.moderation_work.work_id == work_id
            else None
        )

    async def delete_moderated(
        self, target: ModeratedWorkTarget, moderator_id: UUID, reason: str
    ) -> bool:
        self.moderation = (target, moderator_id, reason)
        return True

    async def save_embedding(
        self, work_id: UUID, embedding: list[float], model_name: str
    ) -> None:
        del work_id, model_name
        self.embedding = embedding

    async def search_published(
        self,
        viewer_id: UUID | None,
        embedding: list[float],
        limit: int,
        type_code: str | None,
        min_similarity: float,
        offset: int,
        owner_id: UUID | None = None,
    ) -> list[WorkSearchResponse]:
        del viewer_id
        self.search_limit = limit
        self.search_embedding = embedding
        self.search_type_code = type_code
        self.search_min_similarity = min_similarity
        self.search_offset = offset
        self.search_owner_id = owner_id
        return self.search_results[:limit]

    async def list_unembedded_paths(self, limit: int) -> list[tuple[UUID, str]]:
        return self.unembedded[:limit]


class FakeWorkStorage:
    def __init__(self, exists: bool = True) -> None:
        self.exists = exists
        self.deleted_path: str | None = None

    async def create_signed_upload(self, path: str) -> tuple[str, str]:
        return f"https://storage.test/{path}?token=signed", "signed"

    async def object_exists(self, path: str) -> bool:
        del path
        return self.exists

    async def delete_object(self, path: str) -> None:
        self.deleted_path = path

    def public_url(self, path: str) -> str:
        return f"https://storage.test/{path}"


class FakeEmbeddingProvider:
    model_name = "voyage-test"

    def __init__(self, fails: bool = False) -> None:
        self.fails = fails
        self.query: str | None = None

    async def embed_query(self, query: str) -> list[float]:
        self.query = query
        if self.fails:
            raise RuntimeError("provider unavailable")
        return [0.25, 0.75]

    async def embed_image(self, image_url: str) -> list[float]:
        del image_url
        if self.fails:
            raise RuntimeError("provider unavailable")
        return [0.1, 0.9]


def upload_request(mime_type: str = "image/png") -> CreateWorkUploadRequest:
    return CreateWorkUploadRequest(
        type_id=uuid4(),
        title="My work",
        file_name="work.png",
        mime_type=mime_type,
        file_size=1024,
        links=[
            WorkLinkRequest(
                url=HttpUrl("https://portfolio.example/artwork"), label="Portfolio"
            )
        ],
    )


def test_work_link_accepts_http_and_rejects_unsafe_schemes() -> None:
    assert str(upload_request().links[0].url) == "https://portfolio.example/artwork"

    with pytest.raises(ValidationError):
        CreateWorkUploadRequest.model_validate(
            {
                **upload_request().model_dump(),
                "links": [{"url": "javascript:alert(1)"}],
            }
        )


@pytest.mark.asyncio
async def test_prepare_upload_scopes_storage_path_to_owner() -> None:
    repository = FakeWorkRepository()
    service = WorkService(repository, FakeWorkStorage(), "works")
    owner_id = uuid4()

    result = await service.prepare_upload(owner_id, upload_request())

    assert repository.created is not None
    assert result.work_id == repository.created[0]
    assert result.object_path.startswith(f"{owner_id}/")
    assert result.object_path.endswith(".png")
    assert result.upload_url.endswith("?token=signed")
    assert upload_request().links


@pytest.mark.asyncio
async def test_prepare_upload_rejects_unsupported_files() -> None:
    service = WorkService(FakeWorkRepository(), FakeWorkStorage(), "works")

    with pytest.raises(UnsupportedWorkFileError):
        await service.prepare_upload(uuid4(), upload_request("application/pdf"))


@pytest.mark.asyncio
async def test_publish_requires_uploaded_object() -> None:
    repository = FakeWorkRepository()
    repository.path = f"{uuid4()}/{uuid4()}.png"
    service = WorkService(repository, FakeWorkStorage(exists=False), "works")

    with pytest.raises(WorkNotFoundError):
        await service.publish(uuid4(), uuid4())

    assert repository.published is False


@pytest.mark.asyncio
async def test_empty_public_feed_has_no_cursor() -> None:
    service = WorkService(FakeWorkRepository(), FakeWorkStorage(), "works")

    result = await service.feed(None, 20, datetime.now(timezone.utc))

    assert result.items == []
    assert result.next_cursor is None


@pytest.mark.asyncio
async def test_public_feed_accepts_category_filter() -> None:
    repository = FakeWorkRepository()
    service = WorkService(repository, FakeWorkStorage(), "works")

    result = await service.feed(None, 20, None, "digital-art")

    assert result.items == []
    assert repository.listed_type_code == "digital-art"


@pytest.mark.asyncio
async def test_profile_feed_scopes_posts_to_authenticated_owner() -> None:
    repository = FakeWorkRepository()
    service = WorkService(repository, FakeWorkStorage(), "works")
    user_id = uuid4()

    result = await service.profile_feed(user_id, 50, None)

    assert result.items == []
    assert repository.listed_owner_id == user_id
    assert repository.listed_liked_by_id is None


@pytest.mark.asyncio
async def test_public_profile_feed_uses_profile_owner_and_current_viewer() -> None:
    repository = FakeWorkRepository()
    service = WorkService(repository, FakeWorkStorage(), "works")
    profile_user_id = uuid4()
    viewer_user_id = uuid4()

    result = await service.public_profile_feed(
        profile_user_id, viewer_user_id, 50, None
    )

    assert result.items == []
    assert repository.listed_owner_id == profile_user_id
    assert repository.listed_viewer_id == viewer_user_id


@pytest.mark.asyncio
async def test_profile_likes_scope_uses_authenticated_user() -> None:
    repository = FakeWorkRepository()
    service = WorkService(repository, FakeWorkStorage(), "works")
    user_id = uuid4()

    result = await service.profile_feed(user_id, 50, None, liked=True)

    assert result.items == []
    assert repository.listed_owner_id is None
    assert repository.listed_liked_by_id == user_id


@pytest.mark.asyncio
async def test_profile_saves_scope_uses_authenticated_user() -> None:
    repository = FakeWorkRepository()
    service = WorkService(repository, FakeWorkStorage(), "works")
    user_id = uuid4()

    result = await service.profile_feed(user_id, 50, None, saved=True)

    assert result.items == []
    assert repository.listed_owner_id is None
    assert repository.listed_liked_by_id is None
    assert repository.listed_saved_by_id == user_id


@pytest.mark.asyncio
async def test_save_delegates_authenticated_user_scope() -> None:
    repository = FakeWorkRepository()
    service = WorkService(repository, FakeWorkStorage(), "works")

    await service.save(uuid4(), uuid4(), True)

    assert repository.saved is True


@pytest.mark.asyncio
async def test_owner_can_update_metadata_without_an_image_field() -> None:
    repository = FakeWorkRepository()
    service = WorkService(repository, FakeWorkStorage(), "works")
    request = UpdateWorkRequest(
        type_id=uuid4(),
        title="Updated title",
        description="Updated description",
        links=[],
    )

    await service.update(uuid4(), uuid4(), request)

    assert repository.updated == request
    assert "image" not in UpdateWorkRequest.model_json_schema()["properties"]


@pytest.mark.asyncio
async def test_delete_removes_storage_before_cascading_database_delete() -> None:
    events: list[str] = []

    class OrderedRepository(FakeWorkRepository):
        async def delete_owned(self, work_id: UUID, owner_id: UUID) -> bool:
            events.append("database")
            return await super().delete_owned(work_id, owner_id)

    class OrderedStorage(FakeWorkStorage):
        async def delete_object(self, path: str) -> None:
            events.append("storage")
            await super().delete_object(path)

    repository = OrderedRepository()
    repository.owned_path = "owner/work.png"
    storage = OrderedStorage()
    service = WorkService(repository, storage, "works")

    await service.delete(uuid4(), uuid4())

    assert events == ["storage", "database"]
    assert storage.deleted_path == "owner/work.png"
    assert repository.deleted is True


@pytest.mark.asyncio
async def test_delete_rejects_non_owner_without_touching_storage() -> None:
    repository = FakeWorkRepository()
    storage = FakeWorkStorage()
    service = WorkService(repository, storage, "works")

    with pytest.raises(WorkNotFoundError):
        await service.delete(uuid4(), uuid4())

    assert storage.deleted_path is None
    assert repository.deleted is False


@pytest.mark.asyncio
async def test_moderator_delete_requires_reason_and_records_actor_before_database_delete() -> (
    None
):
    repository = FakeWorkRepository()
    work_id, owner_id, moderator_id, type_id = uuid4(), uuid4(), uuid4(), uuid4()
    repository.moderation_work = ModeratedWorkTarget(
        work_id=work_id,
        owner_user_id=owner_id,
        type_id=type_id,
        title="Moderated work",
        description="Policy violation",
        storage_bucket="works",
        storage_path=f"{owner_id}/{work_id}.png",
        mime_type="image/png",
    )
    storage = FakeWorkStorage()
    service = WorkService(repository, storage, "works")
    request = ModerateWorkDeletionRequest(reason="  Violates   publication policy. ")

    await service.delete_as_moderator(work_id, moderator_id, request)

    assert storage.deleted_path == repository.moderation_work.storage_path
    assert repository.moderation == (
        repository.moderation_work,
        moderator_id,
        "Violates publication policy.",
    )


def test_moderator_deletion_reason_is_required_and_bounded() -> None:
    with pytest.raises(ValidationError):
        ModerateWorkDeletionRequest(reason="too short")
    with pytest.raises(ValidationError):
        ModerateWorkDeletionRequest(reason="x" * 1001)


@pytest.mark.asyncio
async def test_search_normalizes_query_and_uses_multimodal_embedding() -> None:
    repository = FakeWorkRepository()
    provider = FakeEmbeddingProvider()
    service = WorkService(repository, FakeWorkStorage(), "works", provider, 0.31)

    result = await service.search("  moon   at night ", None, 20, "photography")

    assert result.items == []
    assert provider.query == "moon at night"
    assert repository.search_embedding == [0.25, 0.75]
    assert repository.search_type_code == "photography"
    assert repository.search_min_similarity == 0.31
    assert repository.search_offset == 0
    assert repository.search_limit == 21
    assert result.next_cursor is None


@pytest.mark.asyncio
async def test_search_can_be_scoped_to_a_selected_account() -> None:
    repository = FakeWorkRepository()
    owner_id = uuid4()
    service = WorkService(
        repository, FakeWorkStorage(), "works", FakeEmbeddingProvider()
    )

    await service.search("black cat", None, 20, owner_id=owner_id)

    assert repository.search_owner_id == owner_id


@pytest.mark.asyncio
async def test_feed_can_list_all_works_for_a_selected_account() -> None:
    repository = FakeWorkRepository()
    owner_id = uuid4()
    service = WorkService(repository, FakeWorkStorage(), "works")

    await service.feed(None, 20, None, owner_id=owner_id)

    assert repository.listed_owner_id == owner_id


@pytest.mark.asyncio
async def test_search_returns_a_continuation_cursor_and_continuous_ranks() -> None:
    repository = FakeWorkRepository()
    repository.search_results = [
        WorkSearchResponse(
            work_id=uuid4(),
            owner_user_id=uuid4(),
            artist_name="InkFig artist",
            type_id=uuid4(),
            type_name_en="Photography",
            type_name_ar="Photography",
            title=f"Work {rank}",
            description="",
            links=[],
            image_url=f"https://storage.test/{rank}.jpg",
            mime_type="image/jpeg",
            like_count=0,
            created_at=datetime.now(timezone.utc),
            search_rank=rank,
            similarity_score=0.9 - (rank / 100),
        )
        for rank in range(21, 24)
    ]
    service = WorkService(
        repository, FakeWorkStorage(), "works", FakeEmbeddingProvider()
    )

    result = await service.search("moon", None, 2, cursor=20)

    assert [item.search_rank for item in result.items] == [21, 22]
    assert result.next_cursor == 22
    assert repository.search_limit == 3
    assert repository.search_offset == 20


def test_work_response_accepts_search_ranking_metadata() -> None:
    response = WorkSearchResponse(
        work_id=uuid4(),
        owner_user_id=uuid4(),
        artist_name="InkFig artist",
        type_id=uuid4(),
        type_name_en="Photography",
        type_name_ar="Photography",
        title="Moon",
        description="",
        links=[],
        image_url="https://storage.test/moon.jpg",
        mime_type="image/jpeg",
        like_count=0,
        created_at=datetime.now(timezone.utc),
        search_rank=1,
        similarity_score=0.91,
    )

    assert response.search_rank == 1
    assert response.similarity_score == 0.91


@pytest.mark.asyncio
async def test_search_backfills_existing_published_artworks() -> None:
    repository = FakeWorkRepository()
    work_id = uuid4()
    repository.unembedded = [(work_id, f"owner/{work_id}.png")]
    provider = FakeEmbeddingProvider()
    service = WorkService(repository, FakeWorkStorage(), "works", provider)

    await service.search("moon", None, 20)

    assert repository.embedding == [0.1, 0.9]


@pytest.mark.asyncio
async def test_search_reports_unavailable_when_voyage_is_not_configured() -> None:
    service = WorkService(FakeWorkRepository(), FakeWorkStorage(), "works")

    with pytest.raises(WorkSearchUnavailableError):
        await service.search("moon", None, 20)


@pytest.mark.asyncio
async def test_publish_succeeds_when_embedding_provider_is_temporarily_down() -> None:
    repository = FakeWorkRepository()
    repository.path = f"{uuid4()}/{uuid4()}.png"
    service = WorkService(
        repository, FakeWorkStorage(), "works", FakeEmbeddingProvider(fails=True)
    )

    await service.publish(uuid4(), uuid4())

    assert repository.published is True
    assert repository.embedding is None
