from database import session, engine, Base
from sqlalchemy import select, func, or_, delete
from models import Vacancy
from schema import VacancyDTO


class VacancyORM:
    @staticmethod
    async def create_table():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @staticmethod
    async def add_vacancy(vacancy_id,
                          name,
                          description,
                          salary_from,
                          salary_to,
                          currency,
                          city,
                          experience,
                          employment,
                          employer,
                          address):
        async with session() as conn:
            vacancy_obj = Vacancy(vacancy_id=vacancy_id,
                                  name=name,
                                  description=description,
                                  salary_from=salary_from,
                                  salary_to=salary_to,
                                  currency=currency,
                                  city=city,
                                  experience=experience,
                                  employment=employment,
                                  employer=employer,
                                  address=address
                                  )
            conn.add(vacancy_obj)
            await conn.commit()

    @staticmethod
    async def check_vacancy_exist(vacancy_id):
        async with session() as conn:
            query = select(Vacancy).where(Vacancy.vacancy_id == vacancy_id)
            res = await conn.execute(query)
            vacancy = res.scalar_one_or_none()
            return vacancy is not None

    @staticmethod
    async def get_all_vacancies():
        async with session() as conn:
            query = select(Vacancy)
            res_orm = await conn.execute(query)
            res = res_orm.scalars().all()
            res_dto = [VacancyDTO.model_validate(row, from_attributes=True) for row in res]
            res_dto = [(i.id, i.vacancy_id) for i in res_dto]
            return res_dto

    @staticmethod
    async def delete_vacancy(vacancy_id):
        async with session() as conn:
            query = delete(Vacancy).where(Vacancy.vacancy_id == vacancy_id)
            await conn.execute(query)
            await conn.commit()

    @staticmethod
    async def vacancy_update(vacancy_id,
                             new_name=None,
                             new_description=None,
                             salary_from=None,
                             salary_to=None,
                             currency=None,
                             city=None,
                             experience=None,
                             employment=None,
                             employer=None,
                             address=None):
        async with session() as conn:
            vacancy = await conn.get(Vacancy, vacancy_id)
            if vacancy:
                if new_name:
                    vacancy.name = new_name

                if new_description:
                    vacancy.description = new_description

                if salary_from:
                    vacancy.salary_from = salary_from

                if salary_to:
                    vacancy.salary_to = salary_to

                if currency:
                    vacancy.currency = currency

                if city:
                    vacancy.city = city

                if experience:
                    vacancy.experience = experience

                if employment:
                    vacancy.employment = employment

                if employer:
                    vacancy.employer = employer

                if address:
                    vacancy.address = address

                await conn.commit()

    @staticmethod
    async def get_vacancies(name=None,
                            salary_from=None,
                            salary_to=None,
                            city=None,
                            experience=None,
                            employment=None,
                            employer=None):
        async with session() as conn:
            query = select(Vacancy)
            if name:
                query = query.filter(or_(
                    func.lower(Vacancy.name).like(f"%{name}%"),
                    func.lower(Vacancy.description).like(f"%{name}%"),
                    Vacancy.name == name
                ))
            if salary_from:
                query = query.filter(Vacancy.salary_from >= salary_from)
            if salary_to:
                query = query.filter(Vacancy.salary_to <= salary_to)
            if city:
                query = query.filter_by(city=city)
            if experience:
                query = query.filter(Vacancy.experience == experience)
            if employment:
                query = query.filter_by(employment=employment)
            if employer:
                query = query.filter_by(employer=employer)
            stmt = await conn.execute(query)
            res_orm = stmt.scalars().all()
            res_dto = [VacancyDTO.model_validate(row, from_attributes=True).model_dump() for row in res_orm]
            return res_dto
