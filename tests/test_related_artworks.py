import base64
import os
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from src.app.services.related_artworks_service import RelatedArtworksService
from src.entities.dto.feed import FeedCardResponse
from src.entities.exceptions.works import WorkNotFoundError
from src.infrastructure.config.settings import get_settings
from src.infrastructure.integrations.supabase_storage import SupabaseWorkStorage
from src.infrastructure.repositories.related_artworks_repository import SqlAlchemyRelatedArtworksRepository
from src.entities.dto.related_artworks import RelatedArtworksResponse
from src.interface.dependencies.authentication import get_optional_user
from src.interface.dependencies.works import get_related_artworks_service
from src.main import create_app


def card() -> FeedCardResponse:
    return FeedCardResponse(work_id=uuid4(), owner_user_id=uuid4(), artist_name="Artist", type_id=uuid4(),
                            type_name_en="Art", type_name_ar="فن", title="Artwork", image_url="https://example.com/art.png",
                            mime_type="image/png", like_count=0, liked_by_me=False, saved_by_me=False, created_at=datetime.now(UTC))


class Repository:
    exists = True
    def __init__(self) -> None:
        self.calls: list[tuple[datetime, int, int]] = []
        self.rows = [card() for _ in range(4)]

    async def available(self, work_id: UUID) -> bool:
        return self.exists

    async def list_related(self, work_id: UUID, viewer: UUID | None, snapshot: datetime, offset: int, limit: int) -> list[FeedCardResponse]:
        self.calls.append((snapshot, offset, limit))
        return self.rows[offset:offset + limit]


@pytest.mark.asyncio
async def test_bounded_pages_keep_the_original_snapshot_and_scope() -> None:
    repository = Repository()
    service = RelatedArtworksService(repository)
    work_id = uuid4()
    first = await service.get(work_id, None, 2)
    assert len(first.items) == 2 and first.next_cursor
    second = await service.get(work_id, None, 2, first.next_cursor)
    assert second.next_cursor is None
    assert not set(item.work_id for item in first.items) & set(item.work_id for item in second.items)
    assert repository.calls[0][0] == repository.calls[1][0]
    assert repository.calls[0][2] == 3
    with pytest.raises(ValueError):
        await service.get(uuid4(), None, 2, first.next_cursor)


@pytest.mark.asyncio
@pytest.mark.parametrize("cursor", ["bad", "", "x" * 513, base64.urlsafe_b64encode(b'{}').decode()])
async def test_invalid_cursor_does_not_query_candidates(cursor: str) -> None:
    repository = Repository()
    with pytest.raises(ValueError):
        await RelatedArtworksService(repository).get(uuid4(), None, 20, cursor)
    assert not repository.calls


@pytest.mark.asyncio
async def test_unavailable_source_and_invalid_limits_fail_closed() -> None:
    repository = Repository(); repository.exists = False
    with pytest.raises(WorkNotFoundError):
        await RelatedArtworksService(repository).get(uuid4(), None)
    for limit in [0, 51]:
        with pytest.raises(ValueError):
            await RelatedArtworksService(repository).get(uuid4(), None, limit)
    assert not repository.calls


def test_related_sql_preserves_visibility_model_compatibility_and_fallback() -> None:
    source = (Path(__file__).parents[1] / "src/infrastructure/repositories/related_artworks_repository.py").read_text(encoding="utf-8")
    for fragment in ["w.work_id<>:id", "w.status='published'", "a.account_status='active'", "e.model_name=source.model_name",
                     "where similarity>=0.20 or same_type", "floor(similarity/0.02)", "limit :limit offset :offset", "cast(:viewer as uuid)"]:
        assert fragment in source
    assert "embed_image" not in source


@pytest.mark.parametrize("status", [200, 400, 404])
def test_related_endpoint_contract_and_personalized_cache_headers(status: int) -> None:
    actor, work_id = uuid4(), uuid4()
    service = AsyncMock()
    service.get.return_value = RelatedArtworksResponse(items=[card()])
    if status == 400:
        service.get.side_effect = ValueError("Invalid related artwork cursor.")
    elif status == 404:
        service.get.side_effect = WorkNotFoundError()
    app = create_app()
    app.dependency_overrides[get_related_artworks_service] = lambda: service
    app.dependency_overrides[get_optional_user] = lambda: actor
    response = TestClient(app).get(f"/api/v1/works/{work_id}/related?limit=4")
    assert response.status_code == status
    service.get.assert_awaited_once_with(work_id, actor, 4, None)
    if status == 200:
        assert response.headers["cache-control"] == "private, no-store"
        assert response.headers["vary"] == "Cookie, Authorization"
        assert len(response.json()["items"]) == 1
    else:
        assert "detail" in response.json()


@pytest.mark.asyncio
@pytest.mark.skipif(os.environ.get("INKFIG_RELATED_DB_TEST") != "1", reason="Opt-in read-only database verification")
async def test_related_query_against_real_database_is_read_only() -> None:
    settings = get_settings()
    if not settings.database_url:
        pytest.skip("Read-only database verification requires a configured DATABASE_URL")
    engine = create_async_engine(settings.database_url)
    try:
        async with engine.connect() as connection:
            transaction = await connection.begin()
            try:
                await connection.execute(text("set transaction read only"))
                work_id = await connection.scalar(text("select w.work_id from works w join user_accounts a on a.user_id=w.owner_user_id where w.status='published' and a.account_status='active' limit 1"))
                if work_id is None:
                    pytest.skip("No published artwork available for read-only verification")
                async with AsyncSession(bind=connection) as session:
                    storage = SupabaseWorkStorage(settings.supabase_url, settings.supabase_secret_key, settings.works_bucket)
                    repository = SqlAlchemyRelatedArtworksRepository(session, storage)
                    assert await repository.available(work_id)
                    rows = await repository.list_related(work_id, None, datetime.now(UTC), 0, 20)
                    assert len(rows) <= 20
                    assert all(item.work_id != work_id for item in rows)
                    assert len({item.work_id for item in rows}) == len(rows)
            finally:
                await transaction.rollback()
    finally:
        await engine.dispose()
