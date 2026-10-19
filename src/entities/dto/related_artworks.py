from pydantic import BaseModel
from src.entities.dto.feed import FeedCardResponse


class RelatedArtworksResponse(BaseModel):
    items: list[FeedCardResponse]
    next_cursor: str | None = None
