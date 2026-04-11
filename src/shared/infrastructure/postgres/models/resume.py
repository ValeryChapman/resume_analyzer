from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Text, func, text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.infrastructure.postgres.models.base import BaseModel

if TYPE_CHECKING:
    from shared.infrastructure.postgres.models.user import User


class ResumeProcessingStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class Resume(BaseModel):
    __tablename__ = "resumes"
    __table_args__ = {"schema": "public"}

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("public.users.id", ondelete="CASCADE"),
        nullable=False,
    )
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    processing_status: Mapped[ResumeProcessingStatus] = mapped_column(
        SQLEnum(ResumeProcessingStatus, name="resume_processing_status"),
        nullable=False,
        server_default=text("'pending'"),
        default=ResumeProcessingStatus.pending,
    )
    processed_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    user: Mapped["User"] = relationship("User", back_populates="resumes")

    def __repr__(self):
        return f"<Resume(id={self.id}, user_id={self.user_id}, status={self.processing_status})>"
