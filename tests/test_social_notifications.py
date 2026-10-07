from pathlib import Path


def test_like_and_save_create_owner_notifications() -> None:
    source = (Path(__file__).resolve().parents[1] / "src" / "infrastructure" / "repositories" / "work_repository.py").read_text(encoding="utf-8")
    assert '"like"' in source
    assert '"save"' in source
    assert "insert into notifications" in source
    assert "owner_id != user_id" in source
