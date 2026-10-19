from datetime import datetime
from typing import Protocol
from uuid import UUID
from src.entities.dto.feed import FeedCardResponse


class RelatedArtworksRepository(Protocol):
    async def available(self, work_id: UUID) -> bool: ...
    async def list_related(self, work_id: UUID, viewer: UUID | None, snapshot: datetime,
                           offset: int, limit: int) -> list[FeedCardResponse]: ...
