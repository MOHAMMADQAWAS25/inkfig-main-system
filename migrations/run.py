import asyncio
import importlib.util
import os
from pathlib import Path
from types import ModuleType

import asyncpg  # type: ignore[import-untyped]


def load_storage_migration(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(f"inkfig_migration_{path.stem}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load storage migration {path.name}.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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
        migration_directory = Path(__file__).parent
        migrations = sorted(
            [*migration_directory.glob("*.sql"), *migration_directory.glob("*_storage.py")],
            key=lambda migration: migration.name,
        )
        for migration in migrations:
            applied = await connection.fetchval(
                "select exists(select 1 from public.schema_migrations where filename=$1)",
                migration.name,
            )
            if applied:
                continue
            async with connection.transaction():
                if migration.suffix == ".sql":
                    await connection.execute(migration.read_text(encoding="utf-8"))
                else:
                    apply = getattr(load_storage_migration(migration), "apply", None)
                    if apply is None:
                        raise RuntimeError(
                            f"Storage migration {migration.name} has no apply function."
                        )
                    await apply(connection)
                await connection.execute(
                    "insert into public.schema_migrations(filename) values($1)",
                    migration.name,
                )
            print(f"Applied {migration.name}")
        tables_ready = await connection.fetchval(
            "select count(*) = 4 from information_schema.tables "
            "where table_schema = 'public' "
            "and table_name = any($1::text[])",
            ["work_types", "works", "work_likes", "work_embeddings"],
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
