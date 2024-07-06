from sqlalchemy.orm import Mapped, mapped_column
from database import Base
from sqlalchemy import Index


class Vacancy(Base):
    __tablename__ = "vacancy"
    id: Mapped[int] = mapped_column(primary_key=True)
    vacancy_id: Mapped[str]
    name: Mapped[str]
    description: Mapped[str | None]
    salary_from: Mapped[int | None]
    salary_to: Mapped[int | None]
    currency: Mapped[str | None]
    city: Mapped[str | None]
    experience: Mapped[str | None]
    employment: Mapped[str | None]
    employer: Mapped[str | None]
    address: Mapped[str | None]

    __table_args__ = (
        Index('idx_name', 'name'),
        Index('idx_id', 'vacancy_id'),
        Index('idx_city', 'city'),
        Index('idx_experience', 'experience'),
        Index('idx_employment', 'employment'),
    )