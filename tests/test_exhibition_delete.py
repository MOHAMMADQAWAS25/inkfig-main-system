from pathlib import Path
from typing import cast
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.services.exhibition_service import ExhibitionService
from src.entities.dto.exhibitions import ExhibitionError
from src.entities.exceptions.works import StorageDeleteError
from src.entities.repositories.exhibitions import ExhibitionRepository
from src.entities.repositories.works import WorkMediaProcessor, WorkStorage
from src.infrastructure.integrations.supabase_storage import SupabaseWorkStorage
from src.infrastructure.repositories.exhibition_repository import SqlAlchemyExhibitionRepository
from fastapi.testclient import TestClient
from src.main import create_app
from src.interface.dependencies.authentication import get_optional_user
from src.interface.dependencies.exhibitions import get_exhibition_service


@pytest.mark.parametrize("status", [204, 401, 403, 404, 503])
def test_delete_endpoint_preserves_success_and_error_contract(status: int) -> None:
    actor, exhibition = uuid4(), uuid4()
    service = AsyncMock()
    if status != 204:
        service.delete.side_effect = ExhibitionError(status, "Deletion failed")
    app = create_app()
    app.dependency_overrides[get_exhibition_service] = lambda: service
    app.dependency_overrides[get_optional_user] = lambda: actor
    response = TestClient(app).delete(f"/api/v1/exhibitions/{exhibition}")
    assert response.status_code == status
    service.delete.assert_awaited_once_with(actor, exhibition)
    if status == 204:
        assert response.content == b""
    else:
        assert response.json() == {"detail": "Deletion failed"}


@pytest.mark.asyncio
@pytest.mark.parametrize("actor_present,allowed,admin,status", [
    (False, True, True, 401), (True, False, True, 403),
    (True, True, False, 403), (True, True, True, 204),
])
async def test_delete_checks_active_permission_and_current_admin_role(
    actor_present: bool, allowed: bool, admin: bool, status: int,
) -> None:
    repo = AsyncMock()
    repo.allowed.return_value = allowed
    repo.is_administrator.return_value = admin
    service = ExhibitionService(cast(ExhibitionRepository, repo), cast(WorkStorage, AsyncMock()), cast(WorkMediaProcessor, AsyncMock()))
    actor, exhibition = uuid4() if actor_present else None, uuid4()
    if status != 204:
        with pytest.raises(ExhibitionError) as caught:
            await service.delete(actor, exhibition)
        assert caught.value.status == status
        repo.delete.assert_not_awaited()
    else:
        await service.delete(actor, exhibition)
        repo.allowed.assert_awaited_once_with(actor, "exhibitions.manage")
        repo.is_administrator.assert_awaited_once_with(actor)
        repo.delete.assert_awaited_once_with(exhibition)


@pytest.mark.asyncio
@pytest.mark.parametrize("path", [None, "event/banner.png"])
async def test_delete_cleans_banner_before_sql_and_preserves_original_works(path: str | None) -> None:
    session = MagicMock(spec=AsyncSession)
    exhibition = uuid4()
    session.scalar = AsyncMock(side_effect=[exhibition, path])
    session.execute, session.commit, session.rollback = AsyncMock(), AsyncMock(), AsyncMock()
    storage = AsyncMock(spec=SupabaseWorkStorage)
    async def cleaned(target: str) -> None:
        assert target == path
        session.execute.assert_not_awaited()
        session.commit.assert_not_awaited()
    storage.delete_object.side_effect = cleaned
    repo = SqlAlchemyExhibitionRepository(cast(AsyncSession, session), storage, storage)
    await repo.delete(exhibition)
    if path:
        storage.delete_object.assert_awaited_once_with(path)
    else:
        storage.delete_object.assert_not_awaited()
    assert "for update" in str(session.scalar.call_args_list[0].args[0])
    assert str(session.execute.call_args.args[0]) == "delete from exhibitions where exhibition_id=:id"
    session.commit.assert_awaited_once()
    session.rollback.assert_not_awaited()
    # Existing database FKs cascade exhibition-owned rows, never original works.
    root = Path(__file__).resolve().parents[1] / "migrations"
    initial = (root / "20261018_013_create_exhibitions.sql").read_text()
    assert initial.count("references public.exhibitions(exhibition_id) on delete cascade") == 2
    assert "references public.exhibitions(exhibition_id) on delete cascade" in (root / "20261018_015_exhibition_withdrawal_requests.sql").read_text()


@pytest.mark.asyncio
@pytest.mark.parametrize("failure", [StorageDeleteError(), RuntimeError("database failure")])
async def test_failed_delete_rolls_back_without_success(failure: Exception) -> None:
    session = MagicMock(spec=AsyncSession)
    exhibition = uuid4()
    session.scalar = AsyncMock(side_effect=[exhibition, "event/banner.png"])
    session.execute, session.commit, session.rollback = AsyncMock(), AsyncMock(), AsyncMock()
    storage = AsyncMock(spec=SupabaseWorkStorage)
    expected: type[Exception]
    if isinstance(failure, StorageDeleteError):
        storage.delete_object.side_effect = failure
        expected = ExhibitionError
    else:
        session.execute.side_effect = failure
        expected = RuntimeError
    repo = SqlAlchemyExhibitionRepository(cast(AsyncSession, session), storage, storage)
    with pytest.raises(expected):
        await repo.delete(exhibition)
    session.commit.assert_not_awaited()
    session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_missing_exhibition_does_not_touch_storage() -> None:
    session = MagicMock(spec=AsyncSession)
    session.scalar = AsyncMock(return_value=None)
    session.rollback = AsyncMock()
    storage = AsyncMock(spec=SupabaseWorkStorage)
    repo = SqlAlchemyExhibitionRepository(cast(AsyncSession, session), storage, storage)
    with pytest.raises(ExhibitionError) as caught:
        await repo.delete(uuid4())
    assert caught.value.status == 404
    storage.delete_object.assert_not_awaited()
