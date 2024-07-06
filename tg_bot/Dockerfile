FROM python:3.12

WORKDIR /tg_bot

COPY requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

COPY . /tg_bot

CMD python main.py
