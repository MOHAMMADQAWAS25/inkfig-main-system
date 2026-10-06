import json
from functools import lru_cache
from typing import Any

import httpx


@lru_cache(maxsize=4)
def _secret_value(secret_id: str) -> str:
    import boto3  # type: ignore[import-not-found]

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
        return await self._embed(
            [{"type": "image_url", "image_url": image_url}],
            input_type="document",
        )

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
