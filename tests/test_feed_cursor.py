import base64
import json
from datetime import UTC, datetime
from uuid import UUID

import pytest

from src.app.services.feed_cursor import (
    InvalidFeedCursorError,
    decode_feed_cursor,
    encode_feed_cursor,
    feed_scope,
)
from src.entities.dto.feed import FeedPosition


def test_feed_cursor_round_trips_microseconds_and_uuid() -> None:
    position = FeedPosition(
        datetime(2026, 10, 11, 10, 30, 1, 123456, tzinfo=UTC), UUID(int=42)
    )
    scope = feed_scope(None, None)
    assert decode_feed_cursor(encode_feed_cursor(position, scope), scope) == position


@pytest.mark.parametrize(
    "payload",
    [
        None,
        {},
        [],
        [1],
        [True, "2026-10-11T00:00:00+00:00", str(UUID(int=1)), "scope"],
        [2, "2026-10-11T00:00:00+00:00", str(UUID(int=1)), "scope"],
        [1, "2026-10-11T00:00:00", str(UUID(int=1)), "scope"],
        [1, "2026-10-11T00:00:00+00:00", "bad-uuid", "scope"],
        [1, 42, str(UUID(int=1)), "scope"],
    ],
)
def test_feed_cursor_rejects_invalid_shapes(payload: object) -> None:
    token = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()
    with pytest.raises(InvalidFeedCursorError):
        decode_feed_cursor(token, "scope")
