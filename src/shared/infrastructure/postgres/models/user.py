from datetime import datetime
from typing import TYPE_CHECKING, List
from uuid import UUID, uuid4

from sqlalchemy import (
    BigInteger,
    DateTime,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.infrastructure.postgres.models.base import BaseModel

if TYPE_CHECKING:
    from shared.infrastructure.postgres.models.resume import Resume
    from shared.infrastructure.postgres.models.vacancy import Vacancy


class User(BaseModel):
    __tablename__ = "users"
    __table_args__ = {"schema": "public"}

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    vacancies: Mapped[List["Vacancy"]] = relationship(
        "Vacancy",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    resumes: Mapped[List["Resume"]] = relationship(
        "Resume",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id})>"
