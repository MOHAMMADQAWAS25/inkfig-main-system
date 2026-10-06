from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.infrastructure.integrations.voyage_embeddings import (
    VoyageMultimodalEmbeddingClient,
)


@pytest.mark.asyncio
async def test_query_embedding_uses_query_input_type() -> None:
    response = MagicMock()
    response.json.return_value = {"data": [{"embedding": [0.1, 0.2]}]}
    response.raise_for_status.return_value = None
    http_client = AsyncMock()
    http_client.post.return_value = response
    context = AsyncMock()
    context.__aenter__.return_value = http_client

    with patch(
        "src.infrastructure.integrations.voyage_embeddings.httpx.AsyncClient",
        return_value=context,
    ):
        client = VoyageMultimodalEmbeddingClient("secret", "", "model", 2)
        result = await client.embed_query("قمر في الليل")

    assert result == [0.1, 0.2]
    payload = http_client.post.call_args.kwargs["json"]
    assert payload["input_type"] == "query"
    assert payload["inputs"][0]["content"][0]["text"] == "قمر في الليل"
