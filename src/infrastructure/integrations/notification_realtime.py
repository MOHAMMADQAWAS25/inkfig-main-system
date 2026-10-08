import asyncio
import json
from uuid import UUID

import boto3  # type: ignore[import-untyped]
from botocore.exceptions import ClientError  # type: ignore[import-untyped]
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.config.settings import get_settings


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
