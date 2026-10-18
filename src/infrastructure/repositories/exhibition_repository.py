from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.dto.exhibitions import (
    Exhibition,
    ExhibitionError,
    ExhibitionInput,
    Submission,
)
from src.infrastructure.integrations.supabase_storage import SupabaseWorkStorage


class SqlAlchemyExhibitionRepository:
    def __init__(
        self,
        session: AsyncSession,
        banners: SupabaseWorkStorage,
        works: SupabaseWorkStorage,
    ) -> None:
        self.session, self.banners, self.works = session, banners, works

    async def allowed(self, user_id: UUID, permission: str) -> bool:
        return bool(
            await self.session.scalar(
                text("""
            select exists(select 1 from user_accounts a join user_roles r on r.user_id=a.user_id
            join role_permissions p on p.role_code=r.role_code
            where a.user_id=:user and a.account_status='active' and a.is_active=true
            and a.email_verified_at is not null and p.permission_code=:permission)
        """),
                {"user": user_id, "permission": permission},
            )
        )

    def exhibition(self, row: RowMapping) -> Exhibition:
        data: dict[str, Any] = dict(row)
        path = data.pop("banner_path")
        now = datetime.now(UTC)
        return Exhibition(
            **data,
            banner_url=self.banners.public_url(path) if path else None,
            participation_open=data["participation_opens_at"]
            <= now
            < data["participation_closes_at"],
        )

    async def list_exhibitions(
        self, limit: int, cursor: int, period: str = "all"
    ) -> list[Exhibition]:
        condition = {"upcoming": "event_at > now()", "past": "event_at <= now()"}.get(
            period, "true"
        )
        order = "asc" if period == "upcoming" else "desc"
        rows = (
            (
                await self.session.execute(
                    text(
                        f"select * from exhibitions where {condition} order by event_at {order},exhibition_id {order} limit :limit offset :cursor"
                    ),
                    {"limit": limit, "cursor": cursor},
                )
            )
            .mappings()
            .all()
        )
        return [self.exhibition(row) for row in rows]

    async def get(self, exhibition_id: UUID) -> Exhibition:
        row = (
            (
                await self.session.execute(
                    text("select * from exhibitions where exhibition_id=:id"),
                    {"id": exhibition_id},
                )
            )
            .mappings()
            .first()
        )
        if row is None:
            raise ExhibitionError(404, "Exhibition not found.")
        return self.exhibition(row)

    async def eligible(
        self,
        user_id: UUID,
        limit: int,
        cursor: int,
        work_id: UUID | None = None,
        exhibition_id: UUID | None = None,
    ) -> list[Exhibition]:
        params = {
            "user": user_id,
            "work": work_id,
            "id": exhibition_id,
            "limit": limit,
            "cursor": cursor,
        }
        if work_id is not None:
            owned = await self.session.scalar(
                text(
                    "select exists(select 1 from works where work_id=:work and owner_user_id=:user and status='published')"
                ),
                params,
            )
            if not owned:
                raise ExhibitionError(404, "Select one of your published works.")
        rows = (
            (
                await self.session.execute(
                    text("""
            select e.* from exhibitions e
            where e.participation_opens_at <= now() and now() < e.participation_closes_at
            and e.event_at > now() and (cast(:id as uuid) is null or e.exhibition_id=:id)
            and not exists(select 1 from exhibition_blocks b where b.exhibition_id=e.exhibition_id and b.user_id=:user)
            and (select count(*) from exhibition_submissions s where s.exhibition_id=e.exhibition_id and s.user_id=:user and s.status in ('pending','approved')) < 10
            and (cast(:work as uuid) is null or not exists(select 1 from exhibition_submissions s where s.exhibition_id=e.exhibition_id and s.work_id=:work))
            order by e.event_at,e.exhibition_id limit :limit offset :cursor
        """),
                    params,
                )
            )
            .mappings()
            .all()
        )
        return [self.exhibition(row) for row in rows]

    async def check_capacity(self, exhibition_id: UUID, user_id: UUID) -> None:
        count = await self.session.scalar(
            text("""select count(*) from exhibition_submissions
            where exhibition_id=:id and user_id=:user and status in ('pending','approved')"""),
            {"id": exhibition_id, "user": user_id},
        )
        if count is not None and count >= 10:
            raise ExhibitionError(
                409,
                "You can have at most 10 pending or approved works in this exhibition.",
            )

    async def save(
        self, user_id: UUID, data: ExhibitionInput, exhibition_id: UUID | None
    ) -> Exhibition:
        params = {**data.model_dump(), "creator": user_id, "id": exhibition_id}
        if exhibition_id:
            statement = """update exhibitions set name=:name,description=:description,event_at=:event_at,
                participation_opens_at=:participation_opens_at,participation_closes_at=:participation_closes_at,
                updated_at=now() where exhibition_id=:id returning *"""
        else:
            statement = """insert into exhibitions(creator_user_id,name,description,event_at,participation_opens_at,participation_closes_at)
                values(:creator,:name,:description,:event_at,:participation_opens_at,:participation_closes_at) returning *"""
        row = (await self.session.execute(text(statement), params)).mappings().first()
        if row is None:
            raise ExhibitionError(404, "Exhibition not found.")
        result = self.exhibition(row)
        await self.session.commit()
        return result

    async def lock(self, exhibition_id: UUID) -> None:
        found = await self.session.scalar(
            text(
                "select exhibition_id from exhibitions where exhibition_id=:id for update"
            ),
            {"id": exhibition_id},
        )
        if found is None:
            raise ExhibitionError(404, "Exhibition not found.")

    async def submit(self, exhibition_id: UUID, user_id: UUID, work_id: UUID) -> None:
        await self.lock(exhibition_id)
        params = {"id": exhibition_id, "user": user_id, "work": work_id}
        opened = await self.session.scalar(
            text(
                "select participation_opens_at <= now() and now() < participation_closes_at from exhibitions where exhibition_id=:id"
            ),
            params,
        )
        if not opened:
            raise ExhibitionError(409, "Participation is not open.")
        blocked = await self.session.scalar(
            text(
                "select exists(select 1 from exhibition_blocks where exhibition_id=:id and user_id=:user)"
            ),
            params,
        )
        if blocked:
            raise ExhibitionError(
                403, "You are blocked from participating in this exhibition."
            )
        owned = await self.session.scalar(
            text(
                "select work_id from works where work_id=:work and owner_user_id=:user and status='published' for share"
            ),
            params,
        )
        if not owned:
            raise ExhibitionError(404, "Select one of your published works.")
        duplicate = await self.session.scalar(
            text(
                "select exists(select 1 from exhibition_submissions where exhibition_id=:id and work_id=:work)"
            ),
            params,
        )
        if duplicate:
            raise ExhibitionError(409, "This work has already been submitted.")
        await self.check_capacity(exhibition_id, user_id)
        try:
            await self.session.execute(
                text(
                    "insert into exhibition_submissions(exhibition_id,work_id,user_id) values(:id,:work,:user)"
                ),
                params,
            )
            await self.session.commit()
        except IntegrityError as error:
            await self.session.rollback()
            raise ExhibitionError(
                409, "This work has already been submitted."
            ) from error

    async def submissions(
        self,
        exhibition_id: UUID,
        viewer: UUID | None,
        scope: str,
        limit: int,
        cursor: int,
        status: str | None = None,
    ) -> list[Submission]:
        condition = (
            "s.status='approved'"
            if scope == "public"
            else "s.user_id=cast(:viewer as uuid)"
            if scope == "mine"
            else "true"
        )
        rows = (
            (
                await self.session.execute(
                    text(f"""
            select s.*,w.title,w.storage_path,p.full_name artist_name from exhibition_submissions s
            join works w on w.work_id=s.work_id join user_profiles p on p.user_id=s.user_id
            join user_accounts a on a.user_id=s.user_id
            where s.exhibition_id=:id and {condition} and a.account_status='active' and w.status='published'
            and (cast(:status as text) is null or s.status=:status)
            {"and not exists(select 1 from exhibition_blocks b where b.exhibition_id=s.exhibition_id and b.user_id=s.user_id)" if scope == "public" else ""}
            order by s.created_at desc,s.submission_id desc limit :limit offset :cursor
        """),
                    {
                        "id": exhibition_id,
                        "viewer": viewer,
                        "limit": limit,
                        "cursor": cursor,
                        "status": status,
                    },
                )
            )
            .mappings()
            .all()
        )
        return [
            Submission(
                **dict(row), image_url=self.works.public_url(row["storage_path"])
            )
            for row in rows
        ]

    async def review(
        self,
        exhibition_id: UUID,
        submission_id: UUID,
        actor: UUID,
        status: str,
        reason: str | None,
    ) -> None:
        await self.lock(exhibition_id)
        if status == "approved":
            previous = (
                (
                    await self.session.execute(
                        text(
                            "select user_id,status from exhibition_submissions where exhibition_id=:id and submission_id=:submission"
                        ),
                        {"id": exhibition_id, "submission": submission_id},
                    )
                )
                .mappings()
                .first()
            )
            if previous is not None and previous["status"] == "rejected":
                await self.check_capacity(exhibition_id, previous["user_id"])
        found = await self.session.scalar(
            text("""update exhibition_submissions set status=:status,rejection_reason=:reason,
            reviewer_user_id=:actor,reviewed_at=now() where exhibition_id=:id and submission_id=:submission
            returning submission_id"""),
            {
                "id": exhibition_id,
                "submission": submission_id,
                "actor": actor,
                "status": status,
                "reason": reason if status == "rejected" else None,
            },
        )
        if found is None:
            raise ExhibitionError(404, "Submission not found.")
        await self.session.commit()

    async def block(
        self, exhibition_id: UUID, user_id: UUID, actor: UUID, reason: str | None
    ) -> None:
        await self.lock(exhibition_id)
        params = {
            "id": exhibition_id,
            "user": user_id,
            "actor": actor,
            "reason": reason,
        }
        if reason is None:
            await self.session.execute(
                text(
                    "delete from exhibition_blocks where exhibition_id=:id and user_id=:user"
                ),
                params,
            )
        else:
            exists = await self.session.scalar(
                text("select user_id from user_accounts where user_id=:user"), params
            )
            if exists is None:
                raise ExhibitionError(404, "Account not found.")
            await self.session.execute(
                text("""insert into exhibition_blocks(exhibition_id,user_id,blocked_by,reason)
                values(:id,:user,:actor,:reason) on conflict(exhibition_id,user_id)
                do update set blocked_by=excluded.blocked_by,reason=excluded.reason,created_at=now()"""),
                params,
            )
        await self.session.commit()

    async def blocks(
        self, exhibition_id: UUID, limit: int, cursor: int
    ) -> list[dict[str, str]]:
        rows = (
            (
                await self.session.execute(
                    text("""select b.user_id,p.full_name,b.reason from exhibition_blocks b
            join user_profiles p on p.user_id=b.user_id where exhibition_id=:id
            order by b.created_at desc,b.user_id desc limit :limit offset :cursor"""),
                    {"id": exhibition_id, "limit": limit, "cursor": cursor},
                )
            )
            .mappings()
            .all()
        )
        return [
            {
                "user_id": str(r["user_id"]),
                "full_name": r["full_name"],
                "reason": r["reason"],
            }
            for r in rows
        ]

    async def banner(self, exhibition_id: UUID, path: str | None) -> str | None:
        await self.lock(exhibition_id)
        old = await self.session.scalar(
            text("select banner_path from exhibitions where exhibition_id=:id"),
            {"id": exhibition_id},
        )
        await self.session.execute(
            text(
                "update exhibitions set banner_path=:path,updated_at=now() where exhibition_id=:id"
            ),
            {"id": exhibition_id, "path": path},
        )
        await self.session.commit()
        return old
