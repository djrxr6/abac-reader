FROM python:3.9-silm-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

RUN python -m pytest

RUN ['python','app.py']
