import asyncio
import json
import logging
from uuid import UUID

import boto3  # type: ignore[import-untyped]
from botocore.exceptions import ClientError  # type: ignore[import-untyped]
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.config.settings import get_settings

logger = logging.getLogger(__name__)


async def publish_exhibitions_changed(session: AsyncSession, exhibition_id: UUID, user_id: UUID | None = None) -> None:
    """Invalidations contain no decision details; REST authorization remains authoritative."""
    endpoint = get_settings().websocket_management_endpoint
    if not endpoint:
        return
    connections = (await session.execute(text("""
        select distinct c.connection_id from websocket_connections c
        join user_accounts a on a.user_id=c.user_id
        where a.account_status='active' and a.is_active=true and a.email_verified_at is not null
        and (c.user_id=cast(:user as uuid) or exists(
            select 1 from user_roles r join role_permissions p on p.role_code=r.role_code
            where r.user_id=c.user_id and p.permission_code='exhibitions.manage'))
    """), {"user": user_id})).scalars().all()
    if not connections:
        return
    client = boto3.client("apigatewaymanagementapi", endpoint_url=endpoint)
    payload = json.dumps({"type": "exhibitions.changed", "exhibition_id": str(exhibition_id)}).encode()
    stale = []
    for connection in connections:
        try:
            await asyncio.to_thread(client.post_to_connection, ConnectionId=connection, Data=payload)
        except ClientError as error:
            if error.response.get("ResponseMetadata", {}).get("HTTPStatusCode") == 410:
                stale.append(connection)
    if stale:
        await session.execute(text("delete from websocket_connections where connection_id=any(:ids)"), {"ids": stale})
        await session.commit()


async def publish_exhibition_updates(session: AsyncSession, exhibition_id: UUID, user_id: UUID | None = None, notification: bool = False) -> None:
    # Called only after the decision + notification commit. Delivery cannot undo it.
    for kind in (["exhibition", "notification"] if notification and user_id else ["exhibition"]):
        try:
            if kind == "notification" and user_id:
                await publish_notifications_changed(session, user_id)
            else:
                await publish_exhibitions_changed(session, exhibition_id, user_id)
        except Exception:
            await session.rollback()
            logger.exception("Exhibition live delivery failed (%s); saved state is unchanged", kind)


async def publish_notifications_changed(session: AsyncSession, user_id: UUID) -> None:
    endpoint = get_settings().websocket_management_endpoint
    if not endpoint:
        return
    connections = (
        (
            await session.execute(
                text(
                    "select connection_id from websocket_connections where user_id=:user_id"
                ),
                {"user_id": user_id},
            )
        )
        .scalars()
        .all()
    )
    if not connections:
        return
    client = boto3.client("apigatewaymanagementapi", endpoint_url=endpoint)
    stale: list[str] = []
    payload = json.dumps({"type": "notifications.changed"}).encode()
    for connection_id in connections:
        try:
            await asyncio.to_thread(
                client.post_to_connection, ConnectionId=connection_id, Data=payload
            )
        except ClientError as error:
            if error.response.get("ResponseMetadata", {}).get("HTTPStatusCode") == 410:
                stale.append(connection_id)
    if stale:
        await session.execute(
            text("delete from websocket_connections where connection_id = any(:ids)"),
            {"ids": stale},
        )
        await session.commit()
