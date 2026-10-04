from dataclasses import dataclass
from typing import Annotated, Callable, Awaitable
from uuid import UUID

import jwt
from fastapi import Depends, Header, HTTPException, Request

from src.infrastructure.config.settings import Settings, get_settings


@dataclass(frozen=True)
class AuthenticatedPrincipal:
    user_id: UUID
    role: str
    permissions: frozenset[str]


async def get_optional_principal(
    settings: Annotated[Settings, Depends(get_settings)],
    request: Request,
    authorization: Annotated[str | None, Header()] = None,
) -> AuthenticatedPrincipal | None:
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
        permissions = claims.get("permissions", [])
        if not isinstance(permissions, list) or not all(isinstance(item, str) for item in permissions):
            raise ValueError
        return AuthenticatedPrincipal(UUID(claims["sub"]), str(claims.get("role", "viewer")), frozenset(permissions))
    except Exception as error:
        raise HTTPException(
            status_code=401, detail="Invalid or expired access token."
        ) from error


async def get_optional_user(
    settings: Annotated[Settings, Depends(get_settings)],
    request: Request,
    authorization: Annotated[str | None, Header()] = None,
) -> UUID | None:
    principal = await get_optional_principal(settings, request, authorization)
    return None if principal is None else principal.user_id


def require_permission(permission: str) -> Callable[..., Awaitable[UUID]]:
    async def dependency(principal: Annotated[AuthenticatedPrincipal | None, Depends(get_optional_principal)]) -> UUID:
        if principal is None:
            raise HTTPException(status_code=401, detail="Authentication is required.")
        if permission not in principal.permissions and "system.manage" not in principal.permissions:
            raise HTTPException(status_code=403, detail="You do not have permission to perform this action.")
        return principal.user_id
    return dependency


async def get_current_user(principal: Annotated[AuthenticatedPrincipal | None, Depends(get_optional_principal)]) -> UUID:
    if principal is None:
        raise HTTPException(status_code=401, detail="Authentication is required.")
    return principal.user_id
