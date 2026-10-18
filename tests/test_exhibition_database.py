"""Opt-in Supabase workflow check. All fixtures and mutations are rolled back."""

import os
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from src.entities.dto.exhibitions import ExhibitionError, ExhibitionInput
from src.infrastructure.config.settings import get_settings
from src.infrastructure.integrations.supabase_storage import SupabaseWorkStorage
from src.infrastructure.repositories.exhibition_repository import (
    SqlAlchemyExhibitionRepository,
)


class RollbackSession(AsyncSession):
    async def commit(self) -> None:
        # Exercise repository SQL without committing the surrounding transaction.
        await self.flush()


@pytest.mark.asyncio
@pytest.mark.skipif(
    os.environ.get("INKFIG_EXHIBITION_DB_TEST") != "1",
    reason="Opt-in rolled-back database verification",
)
async def test_real_database_exhibition_workflow() -> None:
    settings = get_settings()
    engine = create_async_engine(settings.database_url)
    try:
        async with engine.connect() as connection:
            transaction = await connection.begin()
            try:
                async with RollbackSession(bind=connection) as session:
                    manager, student, work = uuid4(), uuid4(), uuid4()
                    for user, role in ((manager, "supervisor"), (student, "user")):
                        email = f"exhibition-test-{user.hex}@hebron.edu"
                        await session.execute(
                            text("""insert into user_accounts(user_id,email,password_hash,is_active,email_verified_at)
                            values(:id,:email,'!unusable-test-password!',true,now())"""),
                            {"id": user, "email": email},
                        )
                        await session.execute(
                            text("""insert into user_profiles(user_id,email,full_name,phone_number,gender,date_of_birth)
                            values(:id,:email,'Exhibition transaction test',:phone,'male','2000-01-01')"""),
                            {
                                "id": user,
                                "email": email,
                                "phone": str(user.int % 10**10).zfill(10),
                            },
                        )
                        await session.execute(
                            text(
                                "insert into user_roles(user_id,role_code) values(:id,:role) on conflict(user_id) do update set role_code=excluded.role_code"
                            ),
                            {"id": user, "role": role},
                        )
                    type_id = await session.scalar(
                        text(
                            "select type_id from work_types where is_active=true limit 1"
                        )
                    )
                    assert type_id is not None
                    await session.execute(
                        text("""insert into works(work_id,owner_user_id,type_id,title,storage_path,mime_type,file_size,status)
                        values(:work,:user,:type,'Transaction-only art',:path,'image/jpeg',100,'published')"""),
                        {
                            "work": work,
                            "user": student,
                            "type": type_id,
                            "path": f"{student}/{work}.jpg",
                        },
                    )
                    banners = SupabaseWorkStorage(
                        settings.supabase_url,
                        settings.supabase_secret_key,
                        "exhibition-banners",
                    )
                    works = SupabaseWorkStorage(
                        settings.supabase_url,
                        settings.supabase_secret_key,
                        settings.works_bucket,
                    )
                    repository = SqlAlchemyExhibitionRepository(session, banners, works)
                    assert await repository.allowed(manager, "exhibitions.manage")
                    assert not await repository.allowed(student, "exhibitions.manage")
                    assert await repository.allowed(student, "exhibitions.participate")
                    now = datetime.now(UTC)
                    exhibition = await repository.save(
                        manager,
                        ExhibitionInput(
                            name="Rollback-only exhibition",
                            description="Never committed",
                            event_at=now + timedelta(days=2),
                            participation_opens_at=now - timedelta(hours=1),
                            participation_closes_at=now + timedelta(days=1),
                        ),
                        None,
                    )
                    exhibition_id = exhibition.exhibition_id
                    assert exhibition.participation_open
                    historical = await repository.save(
                        manager,
                        ExhibitionInput(
                            name="Rollback-only past exhibition",
                            description="Never committed",
                            event_at=now - timedelta(days=1),
                            participation_opens_at=now - timedelta(days=3),
                            participation_closes_at=now - timedelta(days=2),
                        ),
                        None,
                    )
                    upcoming = await repository.list_exhibitions(50, 0, "upcoming")
                    past = await repository.list_exhibitions(50, 0, "past")
                    assert exhibition_id in [item.exhibition_id for item in upcoming]
                    assert historical.exhibition_id not in [
                        item.exhibition_id for item in upcoming
                    ]
                    assert historical.exhibition_id in [
                        item.exhibition_id for item in past
                    ]
                    assert exhibition_id not in [item.exhibition_id for item in past]
                    await repository.submit(exhibition_id, student, work)
                    assert (
                        await repository.submissions(
                            exhibition_id, None, "public", 20, 0
                        )
                        == []
                    )
                    mine = await repository.submissions(
                        exhibition_id, student, "mine", 20, 0
                    )
                    assert len(mine) == 1 and mine[0].status == "pending"
                    submission = mine[0].submission_id
                    await repository.review(
                        exhibition_id,
                        submission,
                        manager,
                        "rejected",
                        "Please follow the theme.",
                    )
                    rejected = await repository.submissions(
                        exhibition_id, student, "mine", 20, 0
                    )
                    assert rejected[0].rejection_reason == "Please follow the theme."
                    await repository.review(
                        exhibition_id, submission, manager, "approved", None
                    )
                    assert (
                        len(
                            await repository.submissions(
                                exhibition_id, None, "public", 20, 0
                            )
                        )
                        == 1
                    )
                    await repository.block(
                        exhibition_id, student, manager, "Exhibition rule violation"
                    )
                    assert (
                        await repository.submissions(
                            exhibition_id, None, "public", 20, 0
                        )
                        == []
                    )
                    with pytest.raises(ExhibitionError, match="blocked"):
                        await repository.submit(exhibition_id, student, work)
                    assert len(await repository.blocks(exhibition_id, 20, 0)) == 1
                    await repository.block(exhibition_id, student, manager, None)
                    assert (
                        len(
                            await repository.submissions(
                                exhibition_id, None, "public", 20, 0
                            )
                        )
                        == 1
                    )
                    await session.execute(
                        text(
                            "update exhibitions set participation_closes_at=now()-interval '1 minute' where exhibition_id=:id"
                        ),
                        {"id": exhibition_id},
                    )
                    with pytest.raises(ExhibitionError, match="not open"):
                        await repository.submit(exhibition_id, student, work)
            finally:
                await transaction.rollback()
    finally:
        await engine.dispose()
