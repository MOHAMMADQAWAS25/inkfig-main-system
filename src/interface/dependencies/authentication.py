from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, Header, HTTPException, Request

from src.infrastructure.config.settings import Settings, get_settings


async def get_optional_user(
    settings: Annotated[Settings, Depends(get_settings)],
    request: Request,
    authorization: Annotated[str | None, Header()] = None,
) -> UUID | None:
    token = request.cookies.get(settings.access_cookie_name)
    if token is None and authorization:
        try:
            scheme, token = authorization.split(" ", 1)
            if scheme.lower() != "bearer":
                raise ValueError
        except ValueError as error:
            raise HTTPException(
                status_code=401, detail="Invalid access token."
            ) from error
    if not token:
        return None
    try:
        claims = jwt.decode(
            token, settings.jwt_secret, algorithms=["HS256"], issuer=settings.jwt_issuer
        )
        if claims.get("type") != "access":
            raise ValueError
        return UUID(claims["sub"])
    except Exception as error:
        raise HTTPException(
            status_code=401, detail="Invalid or expired access token."
        ) from error


async def get_current_user(
    user_id: Annotated[UUID | None, Depends(get_optional_user)],
) -> UUID:
    if user_id is None:
        raise HTTPException(status_code=401, detail="Authentication is required.")
    return user_id
