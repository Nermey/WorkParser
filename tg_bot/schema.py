from pydantic import BaseModel
from typing import Optional


class VacancyDTO(BaseModel):
    id: int
    vacancy_id: str
    name: str
    description: Optional[str]
    salary_from: Optional[int]
    salary_to: Optional[int]
    currency: Optional[str]
    city: Optional[str]
    experience: Optional[str]
    employment: Optional[str]
    employer: Optional[str]
    address: Optional[str]
