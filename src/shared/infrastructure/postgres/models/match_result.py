from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.infrastructure.postgres.models.base import BaseModel

if TYPE_CHECKING:
    from shared.infrastructure.postgres.models.resume import Resume
    from shared.infrastructure.postgres.models.vacancy import Vacancy


class MatchResult(BaseModel):
    __tablename__ = "match_results"
    __table_args__ = (
        UniqueConstraint(
            "vacancy_id", "resume_id", name="uq_match_results_vacancy_resume"
        ),
        {"schema": "public"},
    )

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    vacancy_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("public.vacancies.id", ondelete="CASCADE"),
        nullable=False,
    )
    resume_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("public.resumes.id", ondelete="CASCADE"),
        nullable=False,
    )
    score: Mapped[float] = mapped_column(Float, nullable=False)
    is_suitable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    reasoning: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    vacancy: Mapped["Vacancy"] = relationship(
        "Vacancy",
        back_populates="match_results",
    )
    resume: Mapped["Resume"] = relationship(
        "Resume",
        back_populates="match_results",
    )

    def __repr__(self) -> str:
        return (
            f"<MatchResult(id={self.id}, vacancy_id={self.vacancy_id}, "
            f"resume_id={self.resume_id}, score={self.score})>"
        )
