from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class WorkTypeResponse(BaseModel):
    type_id: UUID
    code: str
    name_en: str
    name_ar: str


class CreateWorkUploadRequest(BaseModel):
    type_id: UUID
    title: str = Field(min_length=1, max_length=160)
    description: str = Field(default="", max_length=2000)
    external_url: HttpUrl | None = None
    file_name: str = Field(min_length=1, max_length=255)
    mime_type: str
    file_size: int = Field(gt=0, le=10_485_760)


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
    external_url: str | None
    image_url: str
    mime_type: str
    like_count: int
    liked_by_me: bool = False
    created_at: datetime


class WorkFeedResponse(BaseModel):
    items: list[WorkResponse]
    next_cursor: datetime | None = None
