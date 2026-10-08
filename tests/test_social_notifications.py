from pathlib import Path


def test_like_and_save_create_owner_notifications() -> None:
    source = (
        Path(__file__).resolve().parents[1]
        / "src"
        / "infrastructure"
        / "repositories"
        / "work_repository.py"
    ).read_text(encoding="utf-8")
    assert '"like"' in source
    assert '"save"' in source
    assert "insert into notifications" in source
    assert "owner_id != user_id" in source
    assert "publish_notifications_changed" in source


def test_main_stack_can_publish_to_shared_websocket_api() -> None:
    root = Path(__file__).resolve().parents[1]
    template = (root / "template.yaml").read_text(encoding="utf-8")
    workflow = (root / ".github" / "workflows" / "deploy.yml").read_text(
        encoding="utf-8"
    )
    assert "NotificationWebSocketApiId" in template
    assert "execute-api:ManageConnections" in template
    assert "NotificationWebSocketApiId" in workflow
