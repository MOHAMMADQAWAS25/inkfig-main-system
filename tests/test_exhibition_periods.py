from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import cast
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.dto.exhibitions import ExhibitionInput
from src.infrastructure.integrations.supabase_storage import SupabaseWorkStorage
from src.infrastructure.repositories.exhibition_repository import SqlAlchemyExhibitionRepository
from src.interface.dependencies.exhibitions import get_exhibition_service
from src.main import create_app


def schedule() -> dict[str, object]:
    start = datetime(2026, 10, 20, 12, tzinfo=UTC)
    return {"name": "Autumn", "description": "Student art", "event_at": start,
            "participation_opens_at": start - timedelta(days=2),
            "participation_closes_at": start - timedelta(days=1)}


@pytest.mark.parametrize("offset", [timedelta(seconds=-1), timedelta(0)])
def test_end_must_be_later_than_start(offset: timedelta) -> None:
    with pytest.raises(ValidationError, match="end after"):
        ExhibitionInput(**schedule(), event_ends_at=datetime(2026, 10, 20, 12, tzinfo=UTC) + offset)  # type: ignore[arg-type]


def test_end_requires_timezone_and_defaults_legacy_payloads_to_24_hours() -> None:
    with pytest.raises(ValidationError, match="timezone"):
        ExhibitionInput(**schedule(), event_ends_at=datetime(2026, 10, 21))  # type: ignore[arg-type]
    legacy = ExhibitionInput(**schedule())  # type: ignore[arg-type]
    assert legacy.event_ends_at == legacy.event_at + timedelta(hours=24)
    explicit = ExhibitionInput(**schedule(), event_ends_at=legacy.event_at + timedelta(days=3))  # type: ignore[arg-type]
    assert explicit.event_ends_at == legacy.event_at + timedelta(days=3)


@pytest.mark.asyncio
@pytest.mark.parametrize("period", ["current", "upcoming", "past"])
async def test_period_filters_apply_before_pagination_with_disjoint_boundaries(period: str) -> None:
    session = MagicMock(spec=AsyncSession)
    result = MagicMock()
    result.mappings.return_value.all.return_value = []
    session.execute = AsyncMock(return_value=result)
    storage = SupabaseWorkStorage("https://storage.test", "test", "works")
    repo = SqlAlchemyExhibitionRepository(cast(AsyncSession, session), storage, storage)
    assert await repo.list_exhibitions(21, 40, period) == []
    query = str(session.execute.call_args.args[0])
    if period == "current":
        assert "event_at <= now() and coalesce(event_ends_at,event_at + interval '24 hours') > now()" in query
    elif period == "past":
        assert "coalesce(event_ends_at,event_at + interval '24 hours') <= now()" in query
    else:
        assert "where event_at > now()" in query
    assert "limit :limit offset :cursor" in query
    assert session.execute.call_args.args[1] == {"limit": 21, "cursor": 40}


def test_current_period_api_contract_and_migration() -> None:
    service = AsyncMock()
    service.list.return_value = {"items": [], "next_cursor": None}
    app = create_app()
    app.dependency_overrides[get_exhibition_service] = lambda: service
    response = TestClient(app).get("/api/v1/exhibitions?period=current&cursor=20")
    assert response.status_code == 200
    service.list.assert_awaited_once_with(20, 20, "current")
    assert TestClient(app).get("/api/v1/exhibitions?period=invalid").status_code == 422
    sql = (Path(__file__).resolve().parents[1] / "migrations/20261020_017_exhibition_end_time.sql").read_text()
    assert "event_ends_at > event_at" in sql
    assert "event_at+interval '24 hours'" in sql
    assert "drop " not in sql.lower()


@pytest.mark.asyncio
async def test_save_persists_the_explicit_end_date() -> None:
    data = ExhibitionInput(**schedule(), event_ends_at=datetime(2026, 10, 24, tzinfo=UTC))  # type: ignore[arg-type]
    session = MagicMock(spec=AsyncSession)
    result = MagicMock()
    row = {**data.model_dump(), "exhibition_id": uuid4(), "creator_user_id": uuid4(), "created_at": data.event_at, "banner_path": None}
    result.mappings.return_value.first.return_value = row
    session.execute, session.commit = AsyncMock(return_value=result), AsyncMock()
    storage = SupabaseWorkStorage("https://storage.test", "test", "works")
    repo = SqlAlchemyExhibitionRepository(cast(AsyncSession, session), storage, storage)
    saved = await repo.save(uuid4(), data, row["exhibition_id"])
    assert saved.event_ends_at == data.event_ends_at
    assert "event_ends_at=:event_ends_at" in str(session.execute.call_args.args[0])
    assert session.execute.call_args.args[1]["event_ends_at"] == data.event_ends_at
