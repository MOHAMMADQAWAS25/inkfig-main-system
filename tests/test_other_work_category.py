from pathlib import Path


def test_other_category_seed_is_localized_and_idempotent() -> None:
    migration = (
        Path(__file__).parents[1]
        / "migrations"
        / "20261018_016_add_other_work_category.sql"
    ).read_text(encoding="utf-8")

    assert "insert into public.work_types" in migration
    assert "('other', 'Other', 'أخرى', true)" in migration
    assert "on conflict (code) do update" in migration
    assert "delete from" not in migration.lower()
