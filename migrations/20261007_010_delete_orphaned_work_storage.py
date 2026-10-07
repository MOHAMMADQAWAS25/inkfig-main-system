import os
from collections.abc import Sequence

import asyncpg  # type: ignore[import-untyped]
import httpx

DELETE_BATCH_SIZE = 100


def _required_environment(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is required for the work-storage cleanup.")
    return value


async def _delete_batch(
    client: httpx.AsyncClient,
    url: str,
    secret: str,
    bucket: str,
    paths: Sequence[str],
) -> None:
    response = await client.request(
        "DELETE",
        f"{url.rstrip('/')}/storage/v1/object/{bucket}",
        headers={"apikey": secret, "Authorization": f"Bearer {secret}"},
        json={"prefixes": list(paths)},
    )
    response.raise_for_status()


async def apply(connection: asyncpg.Connection) -> None:
    url = _required_environment("SUPABASE_URL")
    secret = _required_environment("SUPABASE_SECRET_KEY")
    bucket = os.environ.get("WORKS_BUCKET", "works").strip()
    if bucket != "works":
        raise RuntimeError(
            "Refusing legacy cleanup because WORKS_BUCKET is not exactly 'works'."
        )
    bucket_exists = await connection.fetchval(
        "select exists(select 1 from storage.buckets where id = $1)", bucket
    )
    if not bucket_exists:
        raise RuntimeError("The configured works storage bucket does not exist.")
    orphaned_paths = await connection.fetch(
        """
        select o.name
        from storage.objects o
        where o.bucket_id = $1
          and o.name <> '.emptyFolderPlaceholder'
          and not exists (
              select 1 from public.works w where w.storage_path = o.name
          )
        order by o.name
        """,
        bucket,
    )
    paths = [str(row["name"]) for row in orphaned_paths]
    if any(not path or path.startswith("/") or ".." in path.split("/") for path in paths):
        raise RuntimeError("Unsafe work-storage object path detected; cleanup aborted.")
    async with httpx.AsyncClient(timeout=30) as client:
        for start in range(0, len(paths), DELETE_BATCH_SIZE):
            await _delete_batch(
                client, url, secret, bucket, paths[start : start + DELETE_BATCH_SIZE]
            )
    remaining = await connection.fetchval(
        """
        select count(*)
        from storage.objects o
        where o.bucket_id = $1
          and o.name <> '.emptyFolderPlaceholder'
          and not exists (
              select 1 from public.works w where w.storage_path = o.name
          )
        """,
        bucket,
    )
    if remaining:
        raise RuntimeError(f"{remaining} orphaned work-storage objects remain.")
    print(f"Deleted {len(paths)} orphaned work-storage object(s).")
