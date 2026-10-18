from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.app.services.exhibition_service import ExhibitionService
from src.entities.dto.exhibitions import (
    BannerCompleteInput,
    BannerUploadInput,
    BlockInput,
    Exhibition,
    ExhibitionInput,
    ExhibitionPage,
    ReviewInput,
    SubmissionInput,
    SubmissionPage,
)
from src.interface.dependencies.authentication import get_optional_user
from src.interface.dependencies.exhibitions import get_exhibition_service

router = APIRouter(prefix="/exhibitions", tags=["exhibitions"])
Service = Annotated[ExhibitionService, Depends(get_exhibition_service)]
Actor = Annotated[UUID | None, Depends(get_optional_user)]


@router.get("", response_model=ExhibitionPage)
async def list_exhibitions(
    service: Service,
    limit: int = Query(20, ge=1, le=50),
    cursor: int = Query(0, ge=0, le=100000),
    period: Literal["all", "upcoming", "past"] = "all",
) -> ExhibitionPage:
    return await service.list(limit, cursor, period)


@router.post("", response_model=Exhibition, status_code=201)
async def create_exhibition(
    data: ExhibitionInput, service: Service, actor: Actor
) -> Exhibition:
    return await service.save(actor, data)


@router.get("/{exhibition_id}", response_model=Exhibition)
async def get_exhibition(exhibition_id: UUID, service: Service) -> Exhibition:
    return await service.get(exhibition_id)


@router.put("/{exhibition_id}", response_model=Exhibition)
async def edit_exhibition(
    exhibition_id: UUID, data: ExhibitionInput, service: Service, actor: Actor
) -> Exhibition:
    return await service.save(actor, data, exhibition_id)


@router.post("/{exhibition_id}/submissions", status_code=204)
async def submit(
    exhibition_id: UUID, data: SubmissionInput, service: Service, actor: Actor
) -> None:
    await service.submit(actor, exhibition_id, data.work_id)


@router.get("/{exhibition_id}/submissions", response_model=SubmissionPage)
async def submissions(
    exhibition_id: UUID,
    service: Service,
    actor: Actor,
    scope: Literal["public", "mine", "manage"] = "public",
    limit: int = Query(20, ge=1, le=50),
    cursor: int = Query(0, ge=0, le=100000),
) -> SubmissionPage:
    return await service.submissions(actor, exhibition_id, scope, limit, cursor)


@router.patch("/{exhibition_id}/submissions/{submission_id}", status_code=204)
async def review(
    exhibition_id: UUID,
    submission_id: UUID,
    data: ReviewInput,
    service: Service,
    actor: Actor,
) -> None:
    await service.review(actor, exhibition_id, submission_id, data)


@router.put("/{exhibition_id}/blocks/{user_id}", status_code=204)
async def block(
    exhibition_id: UUID, user_id: UUID, data: BlockInput, service: Service, actor: Actor
) -> None:
    await service.block(actor, exhibition_id, user_id, data.reason)


@router.delete("/{exhibition_id}/blocks/{user_id}", status_code=204)
async def unblock(
    exhibition_id: UUID, user_id: UUID, service: Service, actor: Actor
) -> None:
    await service.block(actor, exhibition_id, user_id, None)


@router.get("/{exhibition_id}/blocks")
async def blocks(
    exhibition_id: UUID,
    service: Service,
    actor: Actor,
    limit: int = Query(20, ge=1, le=50),
    cursor: int = Query(0, ge=0, le=100000),
) -> dict[str, object]:
    return await service.blocks(actor, exhibition_id, limit, cursor)


@router.post("/{exhibition_id}/banner-uploads")
async def prepare_banner(
    exhibition_id: UUID, data: BannerUploadInput, service: Service, actor: Actor
) -> dict[str, str]:
    return await service.prepare_banner(actor, exhibition_id, data)


@router.post("/{exhibition_id}/banner-uploads/complete", status_code=204)
async def complete_banner(
    exhibition_id: UUID, data: BannerCompleteInput, service: Service, actor: Actor
) -> None:
    await service.complete_banner(actor, exhibition_id, data.object_path)
