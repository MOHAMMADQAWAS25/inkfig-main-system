import asyncio
import warnings
from io import BytesIO

import httpx
from PIL import Image, ImageOps, UnidentifiedImageError

from src.entities.dto.media import ImageMedia, ImageSize
from src.entities.exceptions.works import StorageUploadError, UnsupportedWorkFileError
from src.entities.repositories.works import WorkStorage

VARIANT_WIDTHS = (236, 474, 736, 1080)
MAX_IMAGE_PIXELS = 25_000_000


def render_image(data: bytes) -> tuple[int, int, str, list[tuple[int, bytes]]]:
    """Decode once off the event loop; preserve animation through the original URL."""
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(BytesIO(data)) as original:
                if original.format not in {"JPEG", "PNG", "WEBP", "GIF"}:
                    raise UnsupportedWorkFileError
                if original.width * original.height > MAX_IMAGE_PIXELS:
                    raise UnsupportedWorkFileError
                animated = getattr(original, "is_animated", False)
                image = ImageOps.exif_transpose(original).convert("RGBA")
                width, height = image.size
                background = Image.new("RGB", image.size, "#eeeedc")
                background.paste(image, mask=image.getchannel("A"))
                rgb = background.resize((1, 1)).getpixel((0, 0))
                assert isinstance(rgb, tuple)
                color = "#{:02x}{:02x}{:02x}".format(*rgb)
                variants: list[tuple[int, bytes]] = []
                if not animated:
                    for target in sorted({min(width, w) for w in VARIANT_WIDTHS}):
                        resized = image.resize(
                            (target, max(1, round(height * target / width))),
                            Image.Resampling.LANCZOS,
                        )
                        output = BytesIO()
                        resized.save(output, "WEBP", quality=80, method=4)
                        variants.append((target, output.getvalue()))
                return width, height, color, variants
    except (
        UnidentifiedImageError,
        OSError,
        ValueError,
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
    ) as error:
        raise UnsupportedWorkFileError from error


class ArtworkMediaProcessor:
    def __init__(self, storage: WorkStorage) -> None:
        self._storage = storage

    async def prepare(self, path: str) -> ImageMedia:
        try:
            data = await self._storage.download_image(path)
            width, height, color, variants = await asyncio.to_thread(render_image, data)
            await asyncio.gather(
                *(
                    self._storage.upload_variant(f"{path}.feed-{w}.webp", content)
                    for w, content in variants
                )
            )
        except httpx.HTTPError as error:
            raise StorageUploadError from error
        sizes = [
            ImageSize(w=w, url=self._storage.public_url(f"{path}.feed-{w}.webp"))
            for w, _ in variants
        ]
        return ImageMedia(
            url=self._storage.public_url(path),
            width=width,
            height=height,
            dominantColor=color,
            sizes=sizes,
        )
