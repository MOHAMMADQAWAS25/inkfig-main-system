from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest
from pydantic import HttpUrl, ValidationError

from src.app.services.work_service import WorkService
from src.entities.dto.works import (
    CreateWorkUploadRequest,
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
        self.unembedded: list[tuple[UUID, str]] = []

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
    ) -> list[WorkSearchResponse]:
        del viewer_id, limit
        self.search_embedding = embedding
        self.search_type_code = type_code
        self.search_min_similarity = min_similarity
        return []

    async def list_unembedded_paths(self, limit: int) -> list[tuple[UUID, str]]:
        return self.unembedded[:limit]


class FakeWorkStorage:
    def __init__(self, exists: bool = True) -> None:
        self.exists = exists

    async def create_signed_upload(self, path: str) -> tuple[str, str]:
        return f"https://storage.test/{path}?token=signed", "signed"

    async def object_exists(self, path: str) -> bool:
        del path
        return self.exists

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
