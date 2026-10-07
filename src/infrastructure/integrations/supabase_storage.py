from urllib.parse import quote

import httpx

from src.entities.exceptions.works import StorageDeleteError, StorageUploadError


class SupabaseWorkStorage:
    def __init__(self, url: str, secret: str, bucket: str) -> None:
        self._url, self._secret, self._bucket = url.rstrip("/"), secret, bucket

    async def create_signed_upload(self, path: str) -> tuple[str, str]:
        endpoint = f"{self._url}/storage/v1/object/upload/sign/{self._bucket}/{quote(path, safe='/')}"
        headers = {"apikey": self._secret, "Authorization": f"Bearer {self._secret}"}
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                endpoint, headers=headers, json={"allowUpsert": False}
            )
        if response.is_error:
            raise StorageUploadError
        data = response.json()
        token = str(data.get("token", ""))
        raw_url = str(data.get("url") or data.get("signedURL") or "")
        if not token or not raw_url:
            raise StorageUploadError
        upload_url = (
            raw_url
            if raw_url.startswith("http")
            else f"{self._url}/storage/v1{raw_url}"
        )
        if "token=" not in upload_url:
            upload_url = (
                f"{upload_url}{'&' if '?' in upload_url else '?'}token={quote(token)}"
            )
        return upload_url, token

    def public_url(self, path: str) -> str:
        return f"{self._url}/storage/v1/object/public/{self._bucket}/{quote(path, safe='/')}"

    async def object_exists(self, path: str) -> bool:
        endpoint = f"{self._url}/storage/v1/object/{self._bucket}/{quote(path, safe='/')}"
        headers = {"apikey": self._secret, "Authorization": f"Bearer {self._secret}"}
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.head(endpoint, headers=headers)
        return response.status_code == 200

    async def delete_object(self, path: str) -> None:
        endpoint = f"{self._url}/storage/v1/object/{self._bucket}"
        headers = {"apikey": self._secret, "Authorization": f"Bearer {self._secret}"}
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.request(
                "DELETE", endpoint, headers=headers, json={"prefixes": [path]}
            )
        if response.is_error or await self.object_exists(path):
            raise StorageDeleteError
