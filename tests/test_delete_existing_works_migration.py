from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_existing_works_resets_use_cascading_parent_delete() -> None:
    for filename in (
        "20261006_007_delete_existing_works.sql",
        "20261007_008_delete_existing_works.sql",
        "20261007_009_delete_works_before_search_retest.sql",
    ):
        migration = (ROOT / "migrations" / filename).read_text(
            encoding="utf-8"
        ).lower()

        assert "delete from public.works" in migration
        assert "truncate" not in migration
        assert "storage.objects" not in migration


def test_legacy_reset_has_a_safe_storage_cleanup_migration() -> None:
    runner = (ROOT / "migrations" / "run.py").read_text(encoding="utf-8")
    cleanup = (
        ROOT
        / "migrations"
        / "20261007_010_delete_orphaned_work_storage.py"
    ).read_text(encoding="utf-8")

    assert 'glob("*_storage.py")' in runner
    assert "not exists" in cleanup.lower()
    assert "public.works" in cleanup
    assert "w.storage_path = o.name" in cleanup
    assert "WORKS_BUCKET is not exactly 'works'" in cleanup
    assert '"prefixes": list(paths)' in cleanup
    assert "orphaned work-storage objects remain" in cleanup


def test_every_work_owned_table_cascades_when_a_work_is_deleted() -> None:
    migration_directory = Path(__file__).parents[1] / "migrations"
    migrations = {
        "work_likes": "20261001_001_create_works.sql",
        "work_links": "20261004_003_create_work_links.sql",
        "work_saves": "20261005_004_create_work_saves.sql",
        "work_embeddings": "20261006_006_add_work_embeddings.sql",
    }

    for table, filename in migrations.items():
        sql = (migration_directory / filename).read_text(encoding="utf-8").lower()
        assert f"{table}" in sql
        assert "references public.works(work_id) on delete cascade" in sql
