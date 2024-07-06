FROM python:3.12

WORKDIR /vacancy

COPY requirements.txt ./requirements.txt

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV VACANCY_SERVICE_PORT=$VACANCY_SERVICE_PORT
ENV VACANCY_HOST=$VACANCY_HOST

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

COPY . /vacancy

CMD gunicorn app:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind $VACANCY_HOST:$VACANCY_SERVICE_PORT
