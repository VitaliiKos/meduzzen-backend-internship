FROM python:3.11-alpine

MAINTAINER Vitalii

ENV PYTHONUNBUFFERED=1

RUN mkdir /app
WORKDIR /app

COPY Pipfile* /tmp

RUN pip install --upgrade pip && pip install pipenv

RUN cd /tmp\
    && pipenv lock\
    && pipenv requirements > requirements.txt\
    && pip install -r requirements.txt
COPY . .

CMD ["python", "run.py", "--host=0.0.0.0", "--port=8000"]