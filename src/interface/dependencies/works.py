from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.services.work_service import WorkService
from src.infrastructure.config.settings import Settings, get_settings
from src.infrastructure.db.postgres.session import get_database_session
from src.infrastructure.integrations.supabase_storage import SupabaseWorkStorage
from src.infrastructure.repositories.work_repository import SqlAlchemyWorkRepository


def get_work_service(
    session: Annotated[AsyncSession, Depends(get_database_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> WorkService:
    storage = SupabaseWorkStorage(
        settings.supabase_url, settings.supabase_secret_key, settings.works_bucket
    )
    return WorkService(
        SqlAlchemyWorkRepository(session, storage), storage, settings.works_bucket
    )
