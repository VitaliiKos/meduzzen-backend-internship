FROM python:3.11-alpine

MAINTAINER Vitalii

ENV PYTHONUNBUFFERED=1

COPY . .
WORKDIR /app

RUN pip install --upgrade pip && pip install pipenv

COPY Pipfile* /tmp

RUN cd /tmp\
    && pipenv lock\
    && pipenv requirements > requirements.txt\
    && pip install -r requirements.txt

CMD ["python", "run.py", "--host=0.0.0.0", "--port=8000"]