### Инструкция по использованию и настройке

### 1. Настройка переменных окружения

- #### Создадите .env файл по шаблону:

        POSTGRES_VACANCY_USER=""
        POSTGRES_VACANCY_PASSWORD=""
        POSTGRES_VACANCY_PORT=""
        VACANCY_HOST=""
        VACANCY_SERVICE_PORT=""
        HH_RU_CLIENT_ID=""
        HH_RU_SECRET_KEY=""
        BOT_TOKEN="
        BOT_PORT=""

- #### 2. Запуск Docker контейнеров

        docker-compose up --build

