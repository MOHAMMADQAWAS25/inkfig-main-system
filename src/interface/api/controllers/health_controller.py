from src.app.services.health_service import HealthService
from src.entities.dto.health import HealthCheckResponse


class HealthController:
    def __init__(self, health_service: HealthService) -> None:
        self._health_service = health_service

    async def check(self) -> HealthCheckResponse:
        return await self._health_service.check()
