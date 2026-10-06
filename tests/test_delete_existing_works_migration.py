from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_existing_works_reset_uses_cascading_parent_delete() -> None:
    migration = (
        ROOT / "migrations" / "20261006_007_delete_existing_works.sql"
    ).read_text(encoding="utf-8").lower()

    assert "delete from public.works" in migration
    assert "truncate" not in migration
    assert "storage.objects" not in migration
