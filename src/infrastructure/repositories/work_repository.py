import math
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import delete, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.dto.works import (
    CreateWorkUploadRequest,
    UpdateWorkRequest,
    WorkResponse,
    WorkSearchResponse,
    WorkTypeResponse,
)
from src.infrastructure.db.postgres.models.work import (
    WorkLikeModel,
    WorkLinkModel,
    WorkModel,
    WorkSaveModel,
    WorkTypeModel,
)
from src.infrastructure.integrations.supabase_storage import SupabaseWorkStorage


class SqlAlchemyWorkRepository:
    def __init__(self, session: AsyncSession, storage: SupabaseWorkStorage) -> None:
        self._session, self._storage = session, storage

    async def list_types(self) -> list[WorkTypeResponse]:
        rows = (
            await self._session.execute(
                select(WorkTypeModel)
                .where(WorkTypeModel.is_active.is_(True))
                .order_by(WorkTypeModel.name_en)
            )
        ).scalars()
        return [
            WorkTypeResponse(
                type_id=r.type_id, code=r.code, name_en=r.name_en, name_ar=r.name_ar
            )
            for r in rows
        ]

    async def create_draft(
        self,
        work_id: UUID,
        owner_id: UUID,
        data: CreateWorkUploadRequest,
        bucket: str,
        path: str,
    ) -> None:
        exists = await self._session.scalar(
            select(WorkTypeModel.type_id).where(
                WorkTypeModel.type_id == data.type_id, WorkTypeModel.is_active.is_(True)
            )
        )
        if exists is None:
            from src.entities.exceptions.works import WorkTypeNotFoundError

            raise WorkTypeNotFoundError
        self._session.add(
            WorkModel(
                work_id=work_id,
                owner_user_id=owner_id,
                type_id=data.type_id,
                title=data.title.strip(),
                description=data.description.strip(),
                storage_bucket=bucket,
                storage_path=path,
                mime_type=data.mime_type,
                file_size=data.file_size,
                status="draft",
            )
        )
        await self._session.flush()
        self._session.add_all(
            WorkLinkModel(
                work_id=work_id,
                url=str(link.url),
                label=link.label.strip() if link.label else None,
                position=position,
            )
            for position, link in enumerate(data.links)
        )
        await self._session.commit()

    async def publish(self, work_id: UUID, owner_id: UUID) -> bool:
        model = await self._session.scalar(
            select(WorkModel).where(
                WorkModel.work_id == work_id,
                WorkModel.owner_user_id == owner_id,
                WorkModel.status == "draft",
            )
        )
        if model is None:
            return False
        model.status, model.published_at = "published", datetime.now(timezone.utc)
        await self._session.commit()
        return True

    async def draft_path(self, work_id: UUID, owner_id: UUID) -> str | None:
        return await self._session.scalar(
            select(WorkModel.storage_path).where(
                WorkModel.work_id == work_id,
                WorkModel.owner_user_id == owner_id,
                WorkModel.status == "draft",
            )
        )

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
        profile_joins: list[str] = []
        filters = ["w.status = 'published'"]
        parameters: dict[str, object] = {"viewer": viewer_id, "limit": limit}

        if type_code is not None:
            filters.append("t.code = :type_code")
            parameters["type_code"] = type_code
        if before is not None:
            filters.append("w.created_at < :before")
            parameters["before"] = before
        if owner_id is not None:
            filters.append("w.owner_user_id = :owner_id")
            parameters["owner_id"] = owner_id
        if liked_by_id is not None:
            profile_joins.append(
                "join work_likes profile_like "
                "on profile_like.work_id = w.work_id "
                "and profile_like.user_id = :liked_by_id"
            )
            parameters["liked_by_id"] = liked_by_id
        if saved_by_id is not None:
            profile_joins.append(
                "join work_saves profile_save "
                "on profile_save.work_id = w.work_id "
                "and profile_save.user_id = :saved_by_id"
            )
            parameters["saved_by_id"] = saved_by_id

        # Only trusted, fixed fragments are interpolated. Optional predicates are
        # omitted instead of expressed as ``parameter is null OR ...`` so Postgres
        # can choose the matching partial/composite index for each feed variant.
        stmt = text(
            f"""
            select
                w.work_id,
                w.owner_user_id,
                coalesce(p.full_name, 'InkFig artist') as artist_name,
                w.type_id,
                t.name_en,
                t.name_ar,
                w.title,
                w.description,
                coalesce(
                    (select jsonb_agg(jsonb_build_object('url', wl.url, 'label', wl.label) order by wl.position)
                     from work_links wl where wl.work_id = w.work_id),
                    '[]'::jsonb
                ) as links,
                w.storage_path,
                w.mime_type,
                w.created_at,
                count(l.user_id) as like_count,
                coalesce(
                    bool_or(l.user_id = cast(:viewer as uuid)),
                    false
                ) as liked,
                exists (
                    select 1 from work_saves viewer_save
                    where viewer_save.work_id = w.work_id
                      and viewer_save.user_id = cast(:viewer as uuid)
                ) as saved
            from works w
            join work_types t on t.type_id = w.type_id
            join user_accounts owner_account on owner_account.user_id = w.owner_user_id and owner_account.account_status = 'active'
            {' '.join(profile_joins)}
            left join user_profiles p on p.user_id = w.owner_user_id
            left join work_likes l on l.work_id = w.work_id
              and exists (select 1 from user_accounts liker_account where liker_account.user_id = l.user_id and liker_account.account_status = 'active')
            where {' and '.join(filters)}
            group by w.work_id, p.full_name, t.type_id
            order by w.created_at desc, w.work_id desc
            limit :limit
            """
        )
        rows = (
            await self._session.execute(stmt, parameters)
        ).mappings()
        return [
            WorkResponse(
                work_id=r.work_id,
                owner_user_id=r.owner_user_id,
                artist_name=r.artist_name,
                type_id=r.type_id,
                type_name_en=r.name_en,
                type_name_ar=r.name_ar,
                title=r.title,
                description=r.description,
                links=r.links,
                image_url=self._storage.public_url(r.storage_path),
                mime_type=r.mime_type,
                like_count=r.like_count,
                liked_by_me=r.liked,
                saved_by_me=r.saved,
                created_at=r.created_at,
            )
            for r in rows
        ]

    async def set_like(self, work_id: UUID, user_id: UUID, liked: bool) -> bool:
        exists = await self._session.scalar(
            select(WorkModel.work_id).where(
                WorkModel.work_id == work_id, WorkModel.status == "published"
            )
        )
        if exists is None:
            return False
        if liked:
            self._session.add(WorkLikeModel(work_id=work_id, user_id=user_id))
            try:
                await self._session.commit()
            except IntegrityError:
                await self._session.rollback()
        else:
            await self._session.execute(
                delete(WorkLikeModel).where(
                    WorkLikeModel.work_id == work_id, WorkLikeModel.user_id == user_id
                )
            )
            await self._session.commit()
        return True

    async def set_save(self, work_id: UUID, user_id: UUID, saved: bool) -> bool:
        exists = await self._session.scalar(
            select(WorkModel.work_id).where(
                WorkModel.work_id == work_id, WorkModel.status == "published"
            )
        )
        if exists is None:
            return False
        if saved:
            self._session.add(WorkSaveModel(work_id=work_id, user_id=user_id))
            try:
                await self._session.commit()
            except IntegrityError:
                await self._session.rollback()
        else:
            await self._session.execute(
                delete(WorkSaveModel).where(
                    WorkSaveModel.work_id == work_id, WorkSaveModel.user_id == user_id
                )
            )
            await self._session.commit()
        return True

    async def update_owned(
        self, work_id: UUID, owner_id: UUID, data: UpdateWorkRequest
    ) -> bool:
        model = await self._session.scalar(
            select(WorkModel).where(
                WorkModel.work_id == work_id,
                WorkModel.owner_user_id == owner_id,
                WorkModel.status == "published",
            )
        )
        type_exists = await self._session.scalar(
            select(WorkTypeModel.type_id).where(
                WorkTypeModel.type_id == data.type_id,
                WorkTypeModel.is_active.is_(True),
            )
        )
        if model is None:
            return False
        if type_exists is None:
            from src.entities.exceptions.works import WorkTypeNotFoundError

            raise WorkTypeNotFoundError
        model.type_id = data.type_id
        model.title = data.title.strip()
        model.description = data.description.strip()
        await self._session.execute(
            delete(WorkLinkModel).where(WorkLinkModel.work_id == work_id)
        )
        self._session.add_all(
            WorkLinkModel(
                work_id=work_id,
                url=str(link.url),
                label=link.label.strip() if link.label else None,
                position=position,
            )
            for position, link in enumerate(data.links)
        )
        await self._session.commit()
        return True

    async def owned_storage_path(self, work_id: UUID, owner_id: UUID) -> str | None:
        return await self._session.scalar(
            select(WorkModel.storage_path).where(
                WorkModel.work_id == work_id,
                WorkModel.owner_user_id == owner_id,
                WorkModel.status == "published",
            )
        )

    async def delete_owned(self, work_id: UUID, owner_id: UUID) -> bool:
        deleted_id = await self._session.scalar(
            delete(WorkModel).where(
                WorkModel.work_id == work_id,
                WorkModel.owner_user_id == owner_id,
            ).returning(WorkModel.work_id)
        )
        await self._session.commit()
        return deleted_id is not None

    async def save_embedding(
        self, work_id: UUID, embedding: list[float], model_name: str
    ) -> None:
        vector = self._vector_literal(embedding)
        await self._session.execute(
            text(
                """
                insert into work_embeddings(work_id, embedding, model_name)
                values (:work_id, cast(:embedding as extensions.vector), :model_name)
                on conflict (work_id) do update set
                    embedding = excluded.embedding,
                    model_name = excluded.model_name,
                    embedded_at = now()
                """
            ),
            {"work_id": work_id, "embedding": vector, "model_name": model_name},
        )
        await self._session.commit()

    async def search_published(
        self,
        viewer_id: UUID | None,
        embedding: list[float],
        limit: int,
        type_code: str | None,
        min_similarity: float,
        offset: int,
        owner_id: UUID | None = None,
    ) -> list[WorkSearchResponse]:
        filters = ["w.status = 'published'"]
        parameters: dict[str, object] = {
            "viewer": viewer_id,
            "embedding": self._vector_literal(embedding),
            "limit": limit,
            "min_similarity": min_similarity,
            "offset": offset,
        }
        if owner_id is not None:
            filters.append("w.owner_user_id = :owner_id")
            parameters["owner_id"] = owner_id
        if type_code is not None:
            filters.append("t.code = :type_code")
            parameters["type_code"] = type_code
        rows = (
            await self._session.execute(
                text(
                    f"""
                    select w.work_id, w.owner_user_id,
                           coalesce(p.full_name, 'InkFig artist') as artist_name,
                           w.type_id, t.name_en, t.name_ar, w.title, w.description,
                           coalesce((select jsonb_agg(jsonb_build_object('url', wl.url, 'label', wl.label) order by wl.position)
                                     from work_links wl where wl.work_id = w.work_id), '[]'::jsonb) as links,
                           w.storage_path, w.mime_type, w.created_at,
                           1 - (e.embedding <=> cast(:embedding as extensions.vector))
                             as similarity_score,
                           count(l.user_id) as like_count,
                           coalesce(bool_or(l.user_id = cast(:viewer as uuid)), false) as liked,
                           exists(select 1 from work_saves s where s.work_id = w.work_id
                                  and s.user_id = cast(:viewer as uuid)) as saved
                    from work_embeddings e
                    join works w on w.work_id = e.work_id
                    join work_types t on t.type_id = w.type_id
                    join user_accounts a on a.user_id = w.owner_user_id and a.account_status = 'active'
                    left join user_profiles p on p.user_id = w.owner_user_id
                    left join work_likes l on l.work_id = w.work_id
                      and exists(select 1 from user_accounts la where la.user_id = l.user_id and la.account_status = 'active')
                    where {' and '.join(filters)}
                      and (1 - (e.embedding <=> cast(:embedding as extensions.vector))) >= :min_similarity
                    group by w.work_id, p.full_name, t.type_id, e.embedding
                    order by e.embedding <=> cast(:embedding as extensions.vector), w.created_at desc
                    limit :limit
                    offset :offset
                    """
                ),
                parameters,
            )
        ).mappings()
        return [
            WorkSearchResponse(
                work_id=r.work_id,
                owner_user_id=r.owner_user_id,
                artist_name=r.artist_name,
                type_id=r.type_id,
                type_name_en=r.name_en,
                type_name_ar=r.name_ar,
                title=r.title,
                description=r.description,
                links=r.links,
                image_url=self._storage.public_url(r.storage_path),
                mime_type=r.mime_type,
                like_count=r.like_count,
                liked_by_me=r.liked,
                saved_by_me=r.saved,
                created_at=r.created_at,
                search_rank=rank,
                similarity_score=float(r.similarity_score),
            )
            for rank, r in enumerate(rows, start=offset + 1)
        ]

    async def list_unembedded_paths(self, limit: int) -> list[tuple[UUID, str]]:
        rows = (
            await self._session.execute(
                text(
                    """
                    select w.work_id, w.storage_path
                    from works w
                    join user_accounts a on a.user_id = w.owner_user_id
                      and a.account_status = 'active'
                    left join work_embeddings e on e.work_id = w.work_id
                    where w.status = 'published' and e.work_id is null
                    order by w.published_at asc nulls first, w.work_id
                    limit :limit
                    """
                ),
                {"limit": limit},
            )
        ).all()
        return [(row.work_id, row.storage_path) for row in rows]

    @staticmethod
    def _vector_literal(embedding: list[float]) -> str:
        if not embedding or any(not math.isfinite(value) for value in embedding):
            raise ValueError("Embedding must contain finite values.")
        return "[" + ",".join(format(value, ".10g") for value in embedding) + "]"
