from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest

from src.app.services.work_service import WorkService
from src.entities.dto.works import (
    CreateWorkUploadRequest,
    WorkResponse,
    WorkTypeResponse,
)
from src.entities.exceptions.works import UnsupportedWorkFileError, WorkNotFoundError


class FakeWorkRepository:
    def __init__(self) -> None:
        self.created: tuple[UUID, UUID, str] | None = None
        self.path: str | None = None
        self.published = False
        self.listed_type_code: str | None = None

    async def list_types(self) -> list[WorkTypeResponse]:
        return []

    async def create_draft(
        self,
        work_id: UUID,
        owner_id: UUID,
        data: CreateWorkUploadRequest,
        bucket: str,
        path: str,
    ) -> None:
        del data, bucket
        self.created = (work_id, owner_id, path)
        self.path = path

    async def publish(self, work_id: UUID, owner_id: UUID) -> bool:
        del work_id, owner_id
        self.published = True
        return True

    async def draft_path(self, work_id: UUID, owner_id: UUID) -> str | None:
        del work_id, owner_id
        return self.path

    async def list_published(
        self,
        viewer_id: UUID | None,
        limit: int,
        before: datetime | None,
        type_code: str | None,
    ) -> list[WorkResponse]:
        del viewer_id, limit, before
        self.listed_type_code = type_code
        return []

    async def set_like(self, work_id: UUID, user_id: UUID, liked: bool) -> bool:
        del work_id, user_id, liked
        return True


class FakeWorkStorage:
    def __init__(self, exists: bool = True) -> None:
        self.exists = exists

    async def create_signed_upload(self, path: str) -> tuple[str, str]:
        return f"https://storage.test/{path}?token=signed", "signed"

    async def object_exists(self, path: str) -> bool:
        del path
        return self.exists


def upload_request(mime_type: str = "image/png") -> CreateWorkUploadRequest:
    return CreateWorkUploadRequest(
        type_id=uuid4(),
        title="My work",
        file_name="work.png",
        mime_type=mime_type,
        file_size=1024,
    )


@pytest.mark.asyncio
async def test_prepare_upload_scopes_storage_path_to_owner() -> None:
    repository = FakeWorkRepository()
    service = WorkService(repository, FakeWorkStorage(), "works")
    owner_id = uuid4()

    result = await service.prepare_upload(owner_id, upload_request())

    assert repository.created is not None
    assert result.work_id == repository.created[0]
    assert result.object_path.startswith(f"{owner_id}/")
    assert result.object_path.endswith(".png")
    assert result.upload_url.endswith("?token=signed")


@pytest.mark.asyncio
async def test_prepare_upload_rejects_unsupported_files() -> None:
    service = WorkService(FakeWorkRepository(), FakeWorkStorage(), "works")

    with pytest.raises(UnsupportedWorkFileError):
        await service.prepare_upload(uuid4(), upload_request("application/pdf"))


@pytest.mark.asyncio
async def test_publish_requires_uploaded_object() -> None:
    repository = FakeWorkRepository()
    repository.path = f"{uuid4()}/{uuid4()}.png"
    service = WorkService(repository, FakeWorkStorage(exists=False), "works")

    with pytest.raises(WorkNotFoundError):
        await service.publish(uuid4(), uuid4())

    assert repository.published is False


@pytest.mark.asyncio
async def test_empty_public_feed_has_no_cursor() -> None:
    service = WorkService(FakeWorkRepository(), FakeWorkStorage(), "works")

    result = await service.feed(None, 20, datetime.now(timezone.utc))

    assert result.items == []
    assert result.next_cursor is None


@pytest.mark.asyncio
async def test_public_feed_accepts_category_filter() -> None:
    repository = FakeWorkRepository()
    service = WorkService(repository, FakeWorkStorage(), "works")

    result = await service.feed(None, 20, None, "digital-art")

    assert result.items == []
    assert repository.listed_type_code == "digital-art"
