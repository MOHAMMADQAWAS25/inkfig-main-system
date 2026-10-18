from datetime import UTC, datetime, timedelta
from typing import cast
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from pydantic import ValidationError

from src.app.services.exhibition_service import ExhibitionService
from src.entities.dto.exhibitions import (
    Exhibition,
    ExhibitionError,
    ExhibitionInput,
    ReviewInput,
)
from src.entities.repositories.exhibitions import ExhibitionRepository
from src.entities.repositories.works import WorkMediaProcessor, WorkStorage


def service() -> tuple[ExhibitionService, AsyncMock]:
    repository = AsyncMock()
    return ExhibitionService(
        cast(ExhibitionRepository, repository),
        cast(WorkStorage, AsyncMock()),
        cast(WorkMediaProcessor, AsyncMock()),
    ), repository


def data() -> ExhibitionInput:
    now = datetime.now(UTC)
    return ExhibitionInput(
        name="Spring art",
        description="Student artworks",
        event_at=now + timedelta(days=4),
        participation_opens_at=now,
        participation_closes_at=now + timedelta(days=3),
    )


def test_exhibition_dates_and_blank_fields_are_rejected() -> None:
    for changes in (
        {"name": "   "},
        {"description": "  "},
        {"participation_closes_at": data().event_at + timedelta(days=1)},
        {"participation_opens_at": data().event_at},
        {"event_at": datetime.now(UTC).replace(tzinfo=None)},
    ):
        with pytest.raises(ValidationError):
            ExhibitionInput(**{**data().model_dump(), **changes})


def test_rejection_requires_a_real_reason() -> None:
    for reason in (None, "", "    "):
        with pytest.raises(ValidationError):
            ReviewInput(status="rejected", reason=reason)
    assert (
        ReviewInput(status="rejected", reason="  Does not fit the theme  ").reason
        == "Does not fit the theme"
    )
    assert ReviewInput(status="approved").reason is None


@pytest.mark.asyncio
async def test_exhibition_sections_preserve_their_own_pagination_scope() -> None:
    app, repo = service()
    item = Exhibition(
        **data().model_dump(),
        exhibition_id=uuid4(),
        creator_user_id=uuid4(),
        created_at=datetime.now(UTC),
    )
    repo.list_exhibitions.return_value = [item, item]
    page = await app.list(1, 20, "past")
    repo.list_exhibitions.assert_awaited_once_with(2, 20, "past")
    assert page.items == [item] and page.next_cursor == 21


@pytest.mark.asyncio
async def test_unauthenticated_or_unprivileged_users_cannot_create() -> None:
    app, repo = service()
    repo.allowed.return_value = False
    for actor, status in ((None, 401), (uuid4(), 403)):
        with pytest.raises(ExhibitionError) as caught:
            await app.save(actor, data())
        assert caught.value.status == status
    repo.save.assert_not_awaited()


@pytest.mark.asyncio
async def test_managers_may_edit_exhibitions_created_by_someone_else() -> None:
    app, repo = service()
    actor, exhibition = uuid4(), uuid4()
    repo.allowed.return_value = True
    await app.save(actor, data(), exhibition)
    repo.allowed.assert_awaited_once_with(actor, "exhibitions.manage")
    assert repo.save.await_args is not None
    assert repo.save.await_args.args[2] == exhibition


@pytest.mark.asyncio
async def test_manager_submission_scope_does_not_leak_to_unprivileged_users() -> None:
    app, repo = service()
    repo.allowed.return_value = False
    with pytest.raises(ExhibitionError) as caught:
        await app.submissions(uuid4(), uuid4(), "manage", 20, 0)
    assert caught.value.status == 403
    repo.submissions.assert_not_awaited()


@pytest.mark.asyncio
async def test_public_submission_scope_is_available_to_guests() -> None:
    app, repo = service()
    repo.submissions.return_value = []
    exhibition = uuid4()
    page = await app.submissions(None, exhibition, "public", 20, 0)
    assert page.items == []
    repo.allowed.assert_not_awaited()
    repo.submissions.assert_awaited_once_with(exhibition, None, "public", 21, 0)


@pytest.mark.asyncio
async def test_submit_checks_permission_and_passes_authenticated_owner() -> None:
    app, repo = service()
    repo.allowed.return_value = True
    actor, exhibition, work = uuid4(), uuid4(), uuid4()
    await app.submit(actor, exhibition, work)
    repo.allowed.assert_awaited_once_with(actor, "exhibitions.participate")
    repo.submit.assert_awaited_once_with(exhibition, actor, work)


@pytest.mark.asyncio
async def test_banner_path_cannot_cross_exhibitions() -> None:
    app, repo = service()
    repo.allowed.return_value = True
    with pytest.raises(ExhibitionError) as caught:
        await app.complete_banner(uuid4(), uuid4(), f"{uuid4()}/image.jpg")
    assert caught.value.status == 422
    repo.banner.assert_not_awaited()


@pytest.mark.asyncio
async def test_manager_cannot_block_their_own_account() -> None:
    app, repo = service()
    repo.allowed.return_value = True
    actor = uuid4()
    with pytest.raises(ExhibitionError) as caught:
        await app.block(actor, uuid4(), actor, "Reason")
    assert caught.value.status == 409
    repo.block.assert_not_awaited()
