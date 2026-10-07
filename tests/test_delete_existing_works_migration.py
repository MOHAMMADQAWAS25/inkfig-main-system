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
