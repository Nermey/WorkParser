from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    POSTGRES_VACANCY_USER = os.getenv("POSTGRES_VACANCY_USER")
    POSTGRES_VACANCY_PASSWORD = os.getenv("POSTGRES_VACANCY_PASSWORD")
    POSTGRES_VACANCY_PORT = os.getenv("POSTGRES_VACANCY_PORT")
    VACANCY_HOST = os.getenv("VACANCY_HOST")
    VACANCY_SERVICE_PORT = os.getenv("VACANCY_SERVICE_PORT")
    HH_RU_CLIENT_ID = os.getenv("HH_RU_CLIENT_ID")
    HH_RU_SECRET_KEY = os.getenv("HH_RU_SECRET_KEY")

    @property
    def VACANCY_SERVICE_URL(self):
        return f"postgresql+asyncpg://{self.POSTGRES_VACANCY_USER}:{self.POSTGRES_VACANCY_PASSWORD}@db_vacancy:{self.POSTGRES_VACANCY_PORT}/db_vacancy"


settings = Settings()
