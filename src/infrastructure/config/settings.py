from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "inkfig-main-system"
    environment: str = "local"
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = ["http://localhost:5173"]
    supabase_url: str = ""
    supabase_secret_key: str = ""
    database_url: str = ""
    jwt_secret: str = ""
    jwt_issuer: str = "inkfig-user-system"
    access_cookie_name: str = "inkfig_access"
    works_bucket: str = "works"
    voyage_api_key: str = ""
    voyage_secret_id: str = ""
    voyage_model: str = "voyage-multimodal-3.5"
    voyage_embedding_dimension: int = 1024
    voyage_min_similarity: float = 0.20
    websocket_management_endpoint: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
