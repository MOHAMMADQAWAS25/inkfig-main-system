import base64
from io import BytesIO
import json
import math
from functools import lru_cache
from typing import Any

import httpx
from PIL import Image, ImageOps


@lru_cache(maxsize=4)
def _secret_value(secret_id: str) -> str:
    import boto3  # type: ignore[import-not-found,import-untyped]

    response = boto3.client("secretsmanager").get_secret_value(SecretId=secret_id)
    raw = str(response.get("SecretString", ""))
    if not raw:
        raise RuntimeError("The Voyage secret is empty.")
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return raw
    if isinstance(value, dict) and value.get("VOYAGE_API_KEY"):
        return str(value["VOYAGE_API_KEY"])
    raise RuntimeError("The Voyage secret does not contain VOYAGE_API_KEY.")


class VoyageMultimodalEmbeddingClient:
    endpoint = "https://api.voyageai.com/v1/multimodalembeddings"
    max_embedding_pixels = 2_000_000
    max_source_pixels = 100_000_000

    def __init__(
        self,
        api_key: str,
        secret_id: str,
        model_name: str,
        dimension: int,
    ) -> None:
        self._api_key = api_key
        self._secret_id = secret_id
        self.model_name = model_name
        self._dimension = dimension

    def _key(self) -> str:
        if self._api_key:
            return self._api_key
        if self._secret_id:
            return _secret_value(self._secret_id)
        raise RuntimeError("Voyage is not configured.")

    async def embed_query(self, query: str) -> list[float]:
        return await self._embed(
            [{"type": "text", "text": query}], input_type="query"
        )

    async def embed_image(self, image_url: str) -> list[float]:
        image_data_url = await self._prepare_image(image_url)
        return await self._embed(
            [{"type": "image_base64", "image_base64": image_data_url}],
            input_type="document",
        )

    async def _prepare_image(self, image_url: str) -> str:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            response = await client.get(image_url)
        response.raise_for_status()
        with Image.open(BytesIO(response.content)) as source:
            source.seek(0)
            image = ImageOps.exif_transpose(source)
            width, height = image.size
            pixels = width * height
            if pixels <= 0 or pixels > self.max_source_pixels:
                raise RuntimeError("Artwork image dimensions are unsafe to process.")
            if pixels > self.max_embedding_pixels:
                scale = math.sqrt(self.max_embedding_pixels / pixels)
                image = image.resize(
                    (max(1, int(width * scale)), max(1, int(height * scale))),
                    Image.Resampling.LANCZOS,
                )
            if image.mode != "RGB":
                if "A" in image.getbands():
                    background = Image.new("RGB", image.size, "white")
                    background.paste(image, mask=image.getchannel("A"))
                    image = background
                else:
                    image = image.convert("RGB")
            output = BytesIO()
            image.save(output, format="JPEG", quality=88, optimize=True)
        encoded = base64.b64encode(output.getvalue()).decode("ascii")
        return f"data:image/jpeg;base64,{encoded}"

    async def _embed(
        self, content: list[dict[str, str]], input_type: str
    ) -> list[float]:
        payload: dict[str, Any] = {
            "inputs": [{"content": content}],
            "model": self.model_name,
            "input_type": input_type,
            "truncation": False,
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                self.endpoint,
                headers={
                    "Authorization": f"Bearer {self._key()}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
        response.raise_for_status()
        data = response.json()
        embedding = data.get("data", [{}])[0].get("embedding", [])
        if not isinstance(embedding, list) or len(embedding) != self._dimension:
            raise RuntimeError("Voyage returned an unexpected embedding dimension.")
        return [float(value) for value in embedding]
