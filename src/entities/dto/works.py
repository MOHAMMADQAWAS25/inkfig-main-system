from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl, model_validator


class WorkTypeResponse(BaseModel):
    type_id: UUID
    code: str
    name_en: str
    name_ar: str


class WorkLinkRequest(BaseModel):
    url: HttpUrl
    label: str | None = Field(default=None, max_length=120)


class WorkLinkResponse(BaseModel):
    url: str
    label: str | None = None


class CreateWorkUploadRequest(BaseModel):
    type_id: UUID
    title: str = Field(min_length=1, max_length=160)
    description: str = Field(default="", max_length=2000)
    links: list[WorkLinkRequest] = Field(default_factory=list, max_length=10)
    file_name: str = Field(min_length=1, max_length=255)
    mime_type: str
    file_size: int = Field(gt=0, le=10_485_760)

    @model_validator(mode="after")
    def links_must_be_unique(self) -> "CreateWorkUploadRequest":
        urls = [str(link.url) for link in self.links]
        if len(urls) != len(set(urls)):
            raise ValueError("Work links must be unique.")
        return self


class WorkUploadResponse(BaseModel):
    work_id: UUID
    object_path: str
    upload_url: str
    upload_token: str


class WorkResponse(BaseModel):
    work_id: UUID
    owner_user_id: UUID
    artist_name: str
    type_id: UUID
    type_name_en: str
    type_name_ar: str
    title: str
    description: str
    links: list[WorkLinkResponse]
    image_url: str
    mime_type: str
    like_count: int
    liked_by_me: bool = False
    saved_by_me: bool = False
    created_at: datetime


class WorkFeedResponse(BaseModel):
    items: list[WorkResponse]
    next_cursor: datetime | None = None


class WorkSearchResponse(WorkResponse):
    search_rank: int = Field(ge=1)
    similarity_score: float = Field(ge=-1.0, le=1.0)


class WorkSearchFeedResponse(BaseModel):
    items: list[WorkSearchResponse]
    next_cursor: int | None = Field(default=None, ge=0)
