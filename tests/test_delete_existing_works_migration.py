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
