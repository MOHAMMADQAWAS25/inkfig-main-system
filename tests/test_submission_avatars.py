from datetime import UTC, datetime
from typing import cast
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.integrations.supabase_storage import SupabaseWorkStorage
from src.infrastructure.repositories.exhibition_repository import (
    SqlAlchemyExhibitionRepository,
)


@pytest.mark.asyncio
@pytest.mark.parametrize("path", [None, "artist/photo one.jpg"])
async def test_submission_avatar_uses_existing_join_and_public_storage_url(
    path: str | None,
) -> None:
    session = MagicMock(spec=AsyncSession)
    result = MagicMock()
    result.mappings.return_value.all.return_value = [{
        "submission_id": UUID(int=1), "work_id": UUID(int=2),
        "user_id": UUID(int=3), "artist_name": "Artist", "title": "Art",
        "storage_path": "art.png", "artist_avatar_path": path,
        "status": "pending", "rejection_reason": None,
        "created_at": datetime(2026, 10, 18, tzinfo=UTC),
    }]
    session.execute = AsyncMock(return_value=result)
    storage = SupabaseWorkStorage("https://storage.test", "unused", "works")
    repository = SqlAlchemyExhibitionRepository(cast(AsyncSession, session), storage, storage)
    items = await repository.submissions(UUID(int=4), UUID(int=5), "manage", 20, 0)
    assert len(items) == 1
    assert items[0].artist_avatar_url == storage.profile_avatar_url(path)
    assert "artist_avatar_path" not in items[0].model_dump()
    query = str(session.execute.call_args.args[0])
    assert "p.avatar_object_path as artist_avatar_path" in query
    assert "a.account_status='active'" in query
    assert "w.status='published'" in query
    session.execute.assert_awaited_once()
