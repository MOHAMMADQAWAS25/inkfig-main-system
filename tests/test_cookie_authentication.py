from uuid import uuid4

import jwt
import pytest
from starlette.requests import Request

from src.infrastructure.config.settings import Settings
from src.interface.dependencies.authentication import get_optional_user


@pytest.mark.asyncio
async def test_access_cookie_authenticates_main_api_request() -> None:
    user_id = uuid4()
    secret = "a-long-test-jwt-secret-with-32-bytes-minimum"
    token = jwt.encode(
        {"sub": str(user_id), "type": "access", "iss": "inkfig-user-system"},
        secret,
        algorithm="HS256",
    )
    request = Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/",
            "headers": [(b"cookie", f"inkfig_access={token}".encode())],
        }
    )

    result = await get_optional_user(Settings(jwt_secret=secret), request)

    assert result == user_id
