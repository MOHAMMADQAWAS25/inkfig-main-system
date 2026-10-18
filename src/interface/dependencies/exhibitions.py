from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.services.exhibition_service import ExhibitionService
from src.infrastructure.config.settings import Settings, get_settings
from src.infrastructure.db.postgres.session import get_database_session
from src.infrastructure.integrations.supabase_storage import SupabaseWorkStorage
from src.infrastructure.integrations.work_media import ArtworkMediaProcessor
from src.infrastructure.repositories.exhibition_repository import (
    SqlAlchemyExhibitionRepository,
)


def get_exhibition_service(
    session: Annotated[AsyncSession, Depends(get_database_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> ExhibitionService:
    banners = SupabaseWorkStorage(
        settings.supabase_url, settings.supabase_secret_key, "exhibition-banners"
    )
    works = SupabaseWorkStorage(
        settings.supabase_url, settings.supabase_secret_key, settings.works_bucket
    )
    return ExhibitionService(
        SqlAlchemyExhibitionRepository(session, banners, works),
        banners,
        ArtworkMediaProcessor(banners),
    )
