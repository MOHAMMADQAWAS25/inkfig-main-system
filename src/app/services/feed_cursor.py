import base64
import binascii
import hashlib
import json
from datetime import UTC, datetime
from uuid import UUID

from src.entities.dto.feed import FeedPosition


class InvalidFeedCursorError(ValueError):
    pass


def feed_scope(type_code: str | None, owner_id: UUID | None) -> str:
    value = json.dumps([type_code, str(owner_id) if owner_id else None])
    return hashlib.sha256(value.encode()).hexdigest()[:24]


def encode_feed_cursor(position: FeedPosition, scope: str) -> str:
    value = [
        1,
        position.created_at.astimezone(UTC).isoformat(),
        str(position.work_id),
        scope,
    ]
    return (
        base64.urlsafe_b64encode(json.dumps(value, separators=(",", ":")).encode())
        .decode()
        .rstrip("=")
    )


def decode_feed_cursor(token: str, scope: str) -> FeedPosition:
    try:
        if not token or len(token) > 512 or not token.isascii():
            raise ValueError
        raw = base64.b64decode(
            token + "=" * (-len(token) % 4), altchars=b"-_", validate=True
        )
        value = json.loads(raw)
        if (
            not isinstance(value, list)
            or len(value) != 4
            or type(value[0]) is not int
            or value[0] != 1
            or value[3] != scope
            or not isinstance(value[1], str)
            or not isinstance(value[2], str)
        ):
            raise ValueError
        created_at = datetime.fromisoformat(value[1])
        if created_at.utcoffset() is None:
            raise ValueError
        return FeedPosition(created_at.astimezone(UTC), UUID(value[2]))
    except (
        ValueError,
        TypeError,
        binascii.Error,
        UnicodeError,
        OverflowError,
    ) as error:
        raise InvalidFeedCursorError("Invalid or incompatible feed cursor.") from error
