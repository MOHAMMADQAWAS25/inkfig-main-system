from datetime import UTC, datetime
from typing import cast
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.dto.feed import FeedPosition
from src.infrastructure.integrations.supabase_storage import SupabaseWorkStorage
from src.infrastructure.repositories.work_repository import SqlAlchemyWorkRepository


@pytest.mark.asyncio
async def test_feed_sql_uses_bound_composite_key_and_limits_before_counting() -> None:
    session = MagicMock(spec=AsyncSession)
    result = MagicMock()
    result.mappings.return_value = []
    session.execute = AsyncMock(return_value=result)
    storage = SupabaseWorkStorage("https://storage.test", "unused", "works")
    repository = SqlAlchemyWorkRepository(cast(AsyncSession, session), storage)
    position = FeedPosition(datetime(2026, 10, 11, tzinfo=UTC), UUID(int=3))
    viewer, owner = UUID(int=100), UUID(int=200)
    assert (
        await repository.list_feed_cards(viewer, 21, position, "digital-art", owner)
        == []
    )
    statement, parameters = session.execute.call_args.args
    query = str(statement)
    assert "(w.created_at, w.work_id) < (:created_at, :work_id)" in query
    assert "order by w.created_at desc, w.work_id desc" in query
    assert query.index("limit :limit") < query.index("select count(*)")
    assert "a.account_status = 'active'" in query
    assert "w.status = 'published'" in query
    assert "offset" not in query.lower()
    assert "description" not in query
    assert "work_links" not in query
    assert parameters == {
        "viewer": viewer,
        "limit": 21,
        "created_at": position.created_at,
        "work_id": position.work_id,
        "type_code": "digital-art",
        "owner_id": owner,
    }
