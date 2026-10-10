from io import BytesIO
from uuid import uuid4

import pytest
from PIL import Image

from src.app.services.work_service import WorkService
from src.entities.exceptions.works import UnsupportedWorkFileError
from src.infrastructure.integrations.work_media import (
    ArtworkMediaProcessor,
    render_image,
)
from tests.test_work_service import FakeWorkRepository, FakeWorkStorage


def png(width: int, height: int) -> bytes:
    output = BytesIO()
    Image.new("RGB", (width, height), "#ff0000").save(output, "PNG")
    return output.getvalue()


def test_dimensions_color_and_variants_preserve_proportions() -> None:
    width, height, color, variants = render_image(png(1200, 600))
    assert (width, height, color) == (1200, 600, "#ff0000")
    assert [w for w, _ in variants] == [236, 474, 736, 1080]
    for w, content in variants:
        with Image.open(BytesIO(content)) as image:
            assert image.size == (w, w // 2)
            assert image.format == "WEBP"


def test_small_image_is_never_upscaled() -> None:
    assert [w for w, _ in render_image(png(100, 50))[3]] == [100]


def test_animation_uses_original_not_static_variants() -> None:
    output = BytesIO()
    first = Image.new("RGB", (40, 60), "red")
    first.save(
        output,
        "GIF",
        save_all=True,
        append_images=[Image.new("RGB", (40, 60), "blue")],
        duration=100,
        loop=0,
    )
    width, height, _, variants = render_image(output.getvalue())
    assert (width, height, variants) == (40, 60, [])


def test_invalid_and_oversized_images_are_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(UnsupportedWorkFileError):
        render_image(b"not an image")
    monkeypatch.setattr(
        "src.infrastructure.integrations.work_media.MAX_IMAGE_PIXELS", 100
    )
    with pytest.raises(UnsupportedWorkFileError):
        render_image(png(11, 10))


@pytest.mark.asyncio
async def test_publication_prepares_and_persists_media_first() -> None:
    class Storage(FakeWorkStorage):
        def __init__(self) -> None:
            super().__init__()
            self.uploaded: list[str] = []

        async def download_image(self, path: str) -> bytes:
            return png(100, 50)

        async def upload_variant(self, path: str, data: bytes) -> None:
            self.uploaded.append(path)

    repository, storage = FakeWorkRepository(), Storage()
    repository.path = "owner/art.png"
    service = WorkService(
        repository, storage, "works", media_processor=ArtworkMediaProcessor(storage)
    )
    await service.publish(uuid4(), uuid4())
    assert repository.published
    assert repository.media.width == 100
    assert storage.uploaded == ["owner/art.png.feed-100.webp"]
