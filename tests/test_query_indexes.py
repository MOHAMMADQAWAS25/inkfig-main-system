from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_query_indexes_match_published_feed_access_paths() -> None:
    migration = (
        ROOT / "migrations" / "20261006_005_optimize_query_indexes.sql"
    ).read_text(encoding="utf-8")

    assert "(created_at desc, work_id desc)" in migration
    assert "(type_id, created_at desc, work_id desc)" in migration
    assert "(owner_user_id, created_at desc, work_id desc)" in migration
    assert migration.count("where status = 'published'") == 3


def test_profile_collection_indexes_are_user_first() -> None:
    migration = (
        ROOT / "migrations" / "20261006_005_optimize_query_indexes.sql"
    ).read_text(encoding="utf-8")

    assert "work_likes (user_id, created_at desc, work_id desc)" in migration
    assert "work_saves (user_id, created_at desc, work_id desc)" in migration
    assert "drop index if exists public.work_links_work_order_idx" in migration


def test_feed_query_uses_index_friendly_optional_predicates() -> None:
    repository = (
        ROOT / "src" / "infrastructure" / "repositories" / "work_repository.py"
    ).read_text(encoding="utf-8")

    assert "parameter is null OR" in repository
    assert "order by w.created_at desc, w.work_id desc" in repository
    assert "cast(:type_code as varchar) is null" not in repository


def test_semantic_search_rejects_weak_matches() -> None:
    repository = (
        ROOT / "src" / "infrastructure" / "repositories" / "work_repository.py"
    ).read_text(encoding="utf-8")

    assert ">= :min_similarity" in repository
    assert "order by e.embedding <=>" in repository
    assert "as similarity_score" in repository
    assert "enumerate(rows, start=1)" in repository
    assert "search_rank=rank" in repository
