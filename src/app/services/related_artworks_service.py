import base64
import binascii
import json
from datetime import UTC, datetime
from uuid import UUID
from src.entities.dto.related_artworks import RelatedArtworksResponse
from src.entities.exceptions.works import WorkNotFoundError
from src.entities.repositories.related_artworks import RelatedArtworksRepository


class RelatedArtworksService:
    def __init__(self, repository: RelatedArtworksRepository) -> None:
        self._repository = repository

    async def get(self, work_id: UUID, viewer: UUID | None, limit: int = 20,
                  cursor: str | None = None) -> RelatedArtworksResponse:
        if not 1 <= limit <= 50:
            raise ValueError("Invalid related artwork limit.")
        snapshot, offset = datetime.now(UTC), 0
        if cursor is not None:
            try:
                if not cursor or len(cursor) > 512:
                    raise ValueError
                value = json.loads(base64.b64decode(cursor + "=" * (-len(cursor) % 4), altchars=b"-_", validate=True))
                if (not isinstance(value, list) or len(value) != 4 or value[0] != 1
                        or value[1] != str(work_id) or type(value[3]) is not int
                        or not 0 <= value[3] <= 10_000):
                    raise ValueError
                snapshot, offset = datetime.fromisoformat(value[2]), value[3]
                if snapshot.utcoffset() is None or snapshot > datetime.now(UTC):
                    raise ValueError
            except (ValueError, TypeError, binascii.Error, UnicodeError, OverflowError) as error:
                raise ValueError("Invalid related artwork cursor.") from error
        if not await self._repository.available(work_id):
            raise WorkNotFoundError
        rows = await self._repository.list_related(work_id, viewer, snapshot, offset, limit + 1)
        next_cursor = None
        if len(rows) > limit and offset + limit <= 10_000:
            next_cursor = base64.urlsafe_b64encode(json.dumps([1, str(work_id), snapshot.isoformat(), offset + limit]).encode()).decode().rstrip("=")
        return RelatedArtworksResponse(items=rows[:limit], next_cursor=next_cursor)
