from typing import Annotated

from fastapi import APIRouter, Depends

from src.entities.dto.health import HealthCheckResponse
from src.interface.api.controllers.health_controller import HealthController
from src.interface.dependencies.health import get_health_controller

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthCheckResponse)
async def health_check(
    controller: Annotated[HealthController, Depends(get_health_controller)],
) -> HealthCheckResponse:
    return await controller.check()
