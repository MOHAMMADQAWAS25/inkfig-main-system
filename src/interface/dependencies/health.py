from typing import Annotated

from fastapi import Depends

from src.app.services.health_service import HealthService
from src.infrastructure.config.settings import Settings, get_settings
from src.interface.api.controllers.health_controller import HealthController


def get_health_service(
    settings: Annotated[Settings, Depends(get_settings)],
) -> HealthService:
    return HealthService(
        service_name=settings.app_name,
        environment=settings.environment,
    )


def get_health_controller(
    health_service: Annotated[HealthService, Depends(get_health_service)],
) -> HealthController:
    return HealthController(health_service=health_service)
