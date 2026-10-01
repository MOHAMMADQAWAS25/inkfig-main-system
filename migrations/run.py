import asyncio
import os
from pathlib import Path

import asyncpg  # type: ignore[import-untyped]


async def run() -> None:
    url = os.environ.get("DATABASE_URL", "").replace(
        "postgresql+asyncpg://", "postgresql://", 1
    )
    if not url:
        raise RuntimeError("DATABASE_URL is required.")
    connection = await asyncpg.connect(url)
    try:
        await connection.execute(
            "create table if not exists public.schema_migrations("
            "filename text primary key, "
            "applied_at timestamptz not null default now())"
        )
        for migration in sorted(Path(__file__).parent.glob("*.sql")):
            applied = await connection.fetchval(
                "select exists(select 1 from public.schema_migrations where filename=$1)",
                migration.name,
            )
            if applied:
                continue
            async with connection.transaction():
                await connection.execute(migration.read_text(encoding="utf-8"))
                await connection.execute(
                    "insert into public.schema_migrations(filename) values($1)",
                    migration.name,
                )
            print(f"Applied {migration.name}")
        tables_ready = await connection.fetchval(
            "select count(*) = 3 from information_schema.tables "
            "where table_schema = 'public' "
            "and table_name = any($1::text[])",
            ["work_types", "works", "work_likes"],
        )
        bucket_ready = await connection.fetchval(
            "select exists(select 1 from storage.buckets "
            "where id = 'works' and public = true)"
        )
        if not tables_ready or not bucket_ready:
            raise RuntimeError("Works database migration verification failed.")
        print("Verified works tables and public storage bucket.")
    finally:
        await connection.close()


if __name__ == "__main__":
    asyncio.run(run())
