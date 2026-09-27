from pydantic import BaseModel


class HealthCheckResponse(BaseModel):
    service: str
    status: str
    environment: str
