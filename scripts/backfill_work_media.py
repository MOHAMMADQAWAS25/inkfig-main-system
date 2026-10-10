"""Resumable, additive media backfill. Run after schema migration, not at import."""

import asyncio
import logging

from sqlalchemy import text

from src.infrastructure.config.settings import get_settings
from src.infrastructure.db.postgres.session import get_database_session
from src.infrastructure.integrations.supabase_storage import SupabaseWorkStorage
from src.infrastructure.integrations.work_media import ArtworkMediaProcessor
from src.infrastructure.repositories.work_repository import SqlAlchemyWorkRepository


async def run() -> None:
    settings = get_settings()
    storage = SupabaseWorkStorage(
        settings.supabase_url, settings.supabase_secret_key, settings.works_bucket
    )
    processor = ArtworkMediaProcessor(storage)
    failures = 0
    after = "00000000-0000-0000-0000-000000000000"
    async for session in get_database_session():
        repository = SqlAlchemyWorkRepository(session, storage)
        while True:
            rows = (
                await session.execute(
                    text(
                        "select work_id, storage_path from works where media is null "
                        "and status = 'published' and work_id > cast(:after as uuid) "
                        "order by work_id limit 25"
                    ),
                    {"after": after},
                )
            ).all()
            if not rows:
                break
            for row in rows:
                after = str(row.work_id)
                try:
                    media = await processor.prepare(row.storage_path)
                    await repository.save_media(row.work_id, media)
                except Exception:
                    await session.rollback()
                    failures += 1
                    logging.getLogger(__name__).exception(
                        "Media backfill failed for %s", row.work_id
                    )
        if failures:
            raise RuntimeError(
                f"{failures} artwork media preparations failed; rerun to retry."
            )
    print("Verified media backfill completed.")


if __name__ == "__main__":
    asyncio.run(run())
