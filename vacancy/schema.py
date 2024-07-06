from pydantic import BaseModel, Field
from typing import Optional


class Area(BaseModel):
    city: str = Field(..., alias="name")


class Salary(BaseModel):
    from_: Optional[int] = Field(..., alias="from")
    to: Optional[int]
    currency: Optional[str]


class Address(BaseModel):
    raw: Optional[str]


class Schedule(BaseModel):
    name: str


class Employer(BaseModel):
    name: str


class Experience(BaseModel):
    name: str


class Employment(BaseModel):
    name: str


class HhRuVacancy(BaseModel):
    id: str
    name: str
    area: Area
    salary: Optional[Salary]
    address: Optional[Address]
    archived: bool
    employer: Employer
    schedule: Schedule
    experience: Experience
    employment: Employment


class VacancyUpdator(HhRuVacancy):
    description: Optional[str]


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
