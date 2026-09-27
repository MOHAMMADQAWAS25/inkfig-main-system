from src.entities.dto.health import HealthCheckResponse


class HealthService:
    def __init__(self, service_name: str, environment: str) -> None:
        self._service_name = service_name
        self._environment = environment

    async def check(self) -> HealthCheckResponse:
        return HealthCheckResponse(
            service=self._service_name,
            status="ok",
            environment=self._environment,
        )
