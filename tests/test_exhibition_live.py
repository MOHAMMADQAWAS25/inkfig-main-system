from datetime import UTC, datetime
from typing import cast
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.services.exhibition_service import ExhibitionService
from src.entities.dto.exhibitions import ExhibitionError
from src.entities.repositories.exhibitions import ExhibitionRepository
from src.entities.repositories.works import WorkMediaProcessor, WorkStorage
from src.infrastructure.integrations.notification_realtime import (
    publish_exhibition_updates,
)
from src.infrastructure.repositories.exhibition_repository import (
    SqlAlchemyExhibitionRepository,
)


def fixture(status: str = "pending") -> tuple[SqlAlchemyExhibitionRepository, AsyncMock, object]:
    session = AsyncMock(spec=AsyncSession)
    result = MagicMock()
    owner = uuid4()
    result.mappings.return_value.first.return_value = {"user_id": owner, "status": status, "rejection_reason": None, "withdrawal_requested_at": datetime.now(UTC)}
    session.execute.return_value = result
    session.scalar.return_value = datetime.now(UTC)
    repo = SqlAlchemyExhibitionRepository(cast(AsyncSession, session), MagicMock(), MagicMock())
    return repo, session, owner


@pytest.mark.asyncio
async def test_pending_counter_requires_manager_permission() -> None:
    repository = AsyncMock()
    service = ExhibitionService(cast(ExhibitionRepository, repository), cast(WorkStorage, AsyncMock()), cast(WorkMediaProcessor, AsyncMock()))
    with pytest.raises(ExhibitionError):
        await service.pending_counts(None)
    repository.allowed.return_value = False
    with pytest.raises(ExhibitionError):
        await service.pending_counts(uuid4())
    repository.pending_counts.assert_not_awaited()
    repository.allowed.return_value = True
    repository.pending_counts.return_value = {"items": [], "total": 0}
    assert await service.pending_counts(uuid4()) == {"items": [], "total": 0}


@pytest.mark.asyncio
async def test_decision_notification_is_inserted_before_commit_and_delivery_after() -> None:
    repo, session, _owner = fixture()
    events: list[str] = []
    async def inserted(*args: object) -> None:
        events.append("notification")
    async def committed() -> None:
        events.append("commit")
    async def published(*args: object, **kwargs: object) -> None:
        events.append("websocket")
    session.commit.side_effect = committed
    with patch.object(repo, "decision_notification", side_effect=inserted) as notification, patch("src.infrastructure.repositories.exhibition_repository.publish_exhibition_updates", side_effect=published):
        await repo.review(uuid4(), uuid4(), uuid4(), "rejected", "Wrong theme")
    assert events == ["notification", "commit", "websocket"]
    assert notification.call_args.args[3] == "submission_rejected"
    assert notification.call_args.args[4] == "Wrong theme"


@pytest.mark.asyncio
async def test_repeated_approval_does_not_create_duplicate_notifications() -> None:
    repo, session, _ = fixture("approved")
    with patch.object(repo, "decision_notification", new_callable=AsyncMock) as notification:
        await repo.review(uuid4(), uuid4(), uuid4(), "approved", None)
    notification.assert_not_awaited()
    session.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_notification_failure_prevents_decision_commit() -> None:
    repo, session, _ = fixture()
    with patch.object(repo, "decision_notification", side_effect=RuntimeError("write failure")), pytest.raises(RuntimeError):
        await repo.review(uuid4(), uuid4(), uuid4(), "rejected", "Wrong theme")
    session.commit.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("status", ["approved", "rejected"])
async def test_withdrawal_notifies_before_membership_removal(status: str) -> None:
    repo, session, _ = fixture("approved")
    with patch("src.infrastructure.repositories.exhibition_repository.publish_exhibition_updates", new_callable=AsyncMock) as publish:
        await repo.review_withdrawal(uuid4(), uuid4(), uuid4(), status, "Decision")
    statements = [str(call.args[0]) for call in session.execute.call_args_list]
    insert = next(i for i, sql in enumerate(statements) if "insert into notifications" in sql)
    audit = next(i for i, sql in enumerate(statements) if "insert into exhibition_withdrawal_audits" in sql)
    assert insert < audit
    assert "s.user_id<>:actor" in statements[insert]
    assert "on conflict do nothing" in statements[insert]
    publish.assert_awaited_once()
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_live_delivery_failure_cannot_fail_saved_decision() -> None:
    session = AsyncMock(spec=AsyncSession)
    with patch("src.infrastructure.integrations.notification_realtime.publish_exhibitions_changed", side_effect=RuntimeError("offline")), patch("src.infrastructure.integrations.notification_realtime.publish_notifications_changed", new_callable=AsyncMock) as notifications:
        await publish_exhibition_updates(session, uuid4(), uuid4(), notification=True)
    notifications.assert_awaited_once()


@pytest.mark.asyncio
async def test_count_totals_and_scope_match_visible_review_queue() -> None:
    repo, session, _ = fixture()
    session.execute.return_value.mappings.return_value.all.return_value = [{"exhibition_id": uuid4(), "submissions": 2, "withdrawals": 3}]
    counts = await repo.pending_counts()
    assert counts["total"] == 5
    sql = str(session.execute.call_args.args[0])
    assert "w.status='published'" in sql and "a.account_status='active'" in sql


@pytest.mark.asyncio
async def test_exhibition_signal_targets_only_verified_managers_or_owner() -> None:
    from src.infrastructure.integrations.notification_realtime import (
        publish_exhibitions_changed,
    )
    session = AsyncMock(spec=AsyncSession)
    session.execute.return_value = MagicMock()
    session.execute.return_value.scalars.return_value.all.return_value = []
    with patch("src.infrastructure.integrations.notification_realtime.get_settings", return_value=MagicMock(websocket_management_endpoint="https://example.test")):
        await publish_exhibitions_changed(session, uuid4(), uuid4())
    sql = str(session.execute.call_args.args[0])
    assert "exhibitions.manage" in sql
    assert "email_verified_at is not null" in sql and "c.user_id=cast(:user as uuid)" in sql
