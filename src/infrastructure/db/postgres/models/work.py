from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.postgres.base import Base


class WorkTypeModel(Base):
    __tablename__ = "work_types"
    type_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name_en: Mapped[str] = mapped_column(String(120), nullable=False)
    name_ar: Mapped[str] = mapped_column(String(120), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)


class WorkModel(Base):
    __tablename__ = "works"
    work_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True)
    owner_user_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), nullable=False, index=True
    )
    type_id: Mapped[UUID] = mapped_column(
        ForeignKey("work_types.type_id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    storage_bucket: Mapped[str] = mapped_column(String(64), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(512), unique=True, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(80), nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class WorkLikeModel(Base):
    __tablename__ = "work_likes"
    __table_args__ = (UniqueConstraint("work_id", "user_id"),)
    work_id: Mapped[UUID] = mapped_column(
        ForeignKey("works.work_id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class WorkLinkModel(Base):
    __tablename__ = "work_links"
    __table_args__ = (UniqueConstraint("work_id", "url"),)
    link_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    work_id: Mapped[UUID] = mapped_column(
        ForeignKey("works.work_id", ondelete="CASCADE"), nullable=False
    )
    url: Mapped[str] = mapped_column(String(2083), nullable=False)
    label: Mapped[str | None] = mapped_column(String(120))
    position: Mapped[int] = mapped_column(nullable=False)
