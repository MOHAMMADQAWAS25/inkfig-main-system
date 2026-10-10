import json

import httpx
import pytest

from src.entities.exceptions.works import UnsupportedWorkFileError
from src.infrastructure.integrations.supabase_storage import SupabaseWorkStorage


@pytest.mark.asyncio
async def test_download_and_upload_variant_headers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    requests: list[httpx.Request] = []

    def handle(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, content=b"image")

    client = httpx.AsyncClient
    transport = httpx.MockTransport(handle)
    monkeypatch.setattr(
        httpx, "AsyncClient", lambda **kwargs: client(transport=transport, **kwargs)
    )
    storage = SupabaseWorkStorage("https://storage.test", "test-secret", "works")
    assert await storage.download_image("owner/art.png") == b"image"
    await storage.upload_variant("owner/art.png.feed-236.webp", b"variant")
    assert requests[1].headers["content-type"] == "image/webp"
    assert "31536000" in requests[1].headers["cache-control"]
    assert requests[1].content == b"variant"


@pytest.mark.asyncio
async def test_delete_removes_only_original_and_its_variants(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    deleted: list[str] = []

    def handle(request: httpx.Request) -> httpx.Response:
        if request.method == "POST":
            assert json.loads(request.content)["prefix"] == "owner"
            return httpx.Response(
                200,
                json=[
                    {"name": "art.png.feed-100.webp"},
                    {"name": "other.png.feed-236.webp"},
                ],
            )
        if request.method == "DELETE":
            deleted.extend(json.loads(request.content)["prefixes"])
            return httpx.Response(200, json=[])
        return httpx.Response(404)

    client = httpx.AsyncClient
    transport = httpx.MockTransport(handle)
    monkeypatch.setattr(
        httpx, "AsyncClient", lambda **kwargs: client(transport=transport, **kwargs)
    )
    await SupabaseWorkStorage(
        "https://storage.test", "test-secret", "works"
    ).delete_object("owner/art.png")
    assert deleted == ["owner/art.png", "owner/art.png.feed-100.webp"]


@pytest.mark.asyncio
async def test_download_enforces_byte_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, content=b"a" * 10_485_761)
    )
    client = httpx.AsyncClient
    monkeypatch.setattr(
        httpx, "AsyncClient", lambda **kwargs: client(transport=transport, **kwargs)
    )
    with pytest.raises(UnsupportedWorkFileError):
        await SupabaseWorkStorage(
            "https://storage.test", "test-secret", "works"
        ).download_image("owner/art.png")
