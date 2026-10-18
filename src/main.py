from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.entities.dto.exhibitions import ExhibitionError
from src.entities.exceptions.works import (
    StorageDeleteError,
    StorageUploadError,
    UnsupportedWorkFileError,
)
from src.infrastructure.config.settings import get_settings
from src.interface.api.routes.exhibitions import router as exhibitions_router
from src.interface.api.routes.feed import router as feed_router
from src.interface.api.routes.health import router as health_router
from src.interface.api.routes.works import router as works_router


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health_router)
    app.include_router(health_router, prefix=settings.api_prefix)
    app.include_router(works_router, prefix=settings.api_prefix)
    app.include_router(feed_router, prefix=settings.api_prefix)
    app.include_router(exhibitions_router, prefix=settings.api_prefix)

    @app.exception_handler(ExhibitionError)
    async def exhibition_error(
        request: Request, error: ExhibitionError
    ) -> JSONResponse:
        return JSONResponse(status_code=error.status, content={"detail": error.detail})

    @app.exception_handler(StorageUploadError)
    @app.exception_handler(StorageDeleteError)
    async def exhibition_storage_error(
        request: Request, error: Exception
    ) -> JSONResponse:
        return JSONResponse(
            status_code=503,
            content={
                "detail": "Image storage is temporarily unavailable. Please retry."
            },
        )

    @app.exception_handler(UnsupportedWorkFileError)
    async def exhibition_image_error(
        request: Request, error: Exception
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422, content={"detail": "Invalid banner image."}
        )

    return app


app = create_app()
