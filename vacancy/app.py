from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from vacancy_orm import VacancyORM
from typing import Optional
import requests
import re
from schema import HhRuVacancy, VacancyUpdator
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from config import settings
from contextlib import asynccontextmanager
from pydantic import ValidationError


@asynccontextmanager
async def lifespan(app: FastAPI):
    await VacancyORM.create_table()
    global vacancy_update_scheduler, token_refresh_scheduler, access_token
    vacancy_update_scheduler.add_job(update_vacancy, IntervalTrigger(hours=8))
    vacancy_update_scheduler.start()
    token_refresh_scheduler.add_job(refresh_token, IntervalTrigger(minutes=10))
    try:
        response = requests.post("https://api.hh.ru/token", params={
            "client_id": settings.HH_RU_CLIENT_ID,
            "client_secret": settings.HH_RU_SECRET_KEY,
            "grant_type": "client_credentials"
        }).json()
        try:
            res = response.get("access_token")
            access_token = res
        except Exception as e:
            raise HTTPException(status_code=500, detail="Early to refresh token")

    except ValidationError as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {e}")

    yield

app = FastAPI(title="WorkParser", lifespan=lifespan)
vacancy_update_scheduler = AsyncIOScheduler()
token_refresh_scheduler = BackgroundScheduler()
access_token = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def add_vacancy(params):
    try:
        hh = requests.get("https://api.hh.ru/vacancies", params=params,
                          headers={"Authorization": f"Bearer {access_token}"}
                          )
    except Exception as e:
        raise HTTPException(status_code=504, detail=f"error add vacancy {e}")

    for item in hh.json()["items"]:
        vacancy = HhRuVacancy(**item)
        if vacancy.archived or await VacancyORM.check_vacancy_exist(vacancy.id):
            continue
        try:
            description = requests.get(f"https://api.hh.ru/vacancies/{vacancy.id}",
                                       headers={"Authorization": f"Bearer {access_token}"}).json()["description"]
        except Exception as e:
            raise HTTPException(status_code=505, detail=f"get description error {e}")
        if description:
            description = re.sub(r" {2}", " ", re.sub(r"<.*?>", "", description).strip())

        salary_from = None
        salary_to = None
        currency = None
        if vacancy.salary:
            salary_from = vacancy.salary.from_
            salary_to = vacancy.salary.to
            currency = vacancy.salary.currency

        experience = None
        if vacancy.experience:
            experience = vacancy.experience.name

        employment = None
        if vacancy.employment:
            employment = vacancy.employment.name

        address = None
        if vacancy.address:
            address = vacancy.address.raw
        try:
            await VacancyORM.add_vacancy(vacancy_id=vacancy.id,
                                         name=vacancy.name,
                                         description=description,
                                         salary_from=salary_from,
                                         salary_to=salary_to,
                                         currency=currency,
                                         city=vacancy.area.city,
                                         experience=experience,
                                         employment=employment,
                                         employer=vacancy.employer.name,
                                         address=address
                                         )
        except Exception as e:
            print("Ошибка при добавлении вакансии")
            print(e)


async def update_vacancy():
    vacancies_id = await VacancyORM.get_all_vacancies()
    for v_id, vacancy_id in vacancies_id:
        try:
            new_vacancy = VacancyUpdator(**requests.get(f"https://api.hh.ru/vacancies/{vacancy_id}",
                                                        headers={"Authorization": f"Bearer {access_token}"}).json())
            if new_vacancy.archived:
                await VacancyORM.delete_vacancy(vacancy_id)
                continue
            description = new_vacancy.description
            if description:
                description = re.sub(r" {2}", " ", re.sub(r"<.*?>", "", description).strip())

            salary_from = None
            salary_to = None
            currency = None
            if new_vacancy.salary:
                salary_from = new_vacancy.salary.from_
                salary_to = new_vacancy.salary.to
                currency = new_vacancy.salary.currency

            experience = None
            if new_vacancy.experience:
                experience = new_vacancy.experience.name

            employment = None
            if new_vacancy.employment:
                employment = new_vacancy.employment.name

            address = None
            if new_vacancy.address:
                address = new_vacancy.address.raw

            await VacancyORM.vacancy_update(v_id,
                                            new_vacancy.name,
                                            description,
                                            salary_from,
                                            salary_to,
                                            currency,
                                            new_vacancy.area.city,
                                            experience,
                                            employment,
                                            new_vacancy.employer.name,
                                            address)
        except Exception as e:
            raise HTTPException(status_code=503, detail={f"error update vacancy {e}"})


def refresh_token():
    global access_token
    try:
        response = requests.post("https://api.hh.ru/token", params={
            "client_id": settings.HH_RU_CLIENT_ID,
            "client_secret": settings.HH_RU_SECRET_KEY,
            "grant_type": "client_credentials"
        }).json()
        access_token = response.get("access_token")
    except Exception as e:
        raise HTTPException(status_code=502, detail={"error access token"})


@app.get("/vacancy")
async def get_vacancy(name: Optional[str] = None,
                      salary_from: Optional[int] = None,
                      salary_to: Optional[int] = None,
                      city: Optional[str] = None,
                      experience: Optional[str] = None,
                      employment: Optional[str] = None,
                      employer: Optional[str] = None):

    vacancies_dto = await VacancyORM.get_vacancies(name,
                                                   salary_from, salary_to,
                                                   city, experience, employment,
                                                   employer)
    if not vacancies_dto:
        params = {
            "text": name,
            "per_page": 30
        }
        params = {k: v for k, v in params.items() if v is not None}
        await add_vacancy(params)

        vacancies_dto = await VacancyORM.get_vacancies(name,
                                                       salary_from, salary_to,
                                                       city, experience, employment,
                                                       employer)
        if not vacancies_dto:
            raise HTTPException(status_code=201, detail={"vacancies not found"})
    return vacancies_dto
