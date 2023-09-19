FROM python:3.11.2-alpine

MAINTAINER Vitalii

ENV PYTHONUNBUFFERED=1

RUN mkdir /fastapi_app
WORKDIR /fastapi_app

# Install system dependencies for PostgreSQL development (if required)
RUN apk update && apk add --no-cache postgresql-dev gcc musl-dev

# Install pipenv
RUN pip install --upgrade pip && pip install pipenv

# Copy the Pipfile and Pipfile.lock into the container
COPY Pipfile Pipfile.lock /fastapi_app/

# Install project dependencies using pipenv
RUN pipenv install --system --deploy --ignore-pipfile
RUN pip install python-multipart python-dotenv

# Copy the rest of the application files into the container
COPY . .

#WORKDIR /fastapi_app/app
WORKDIR app

EXPOSE ${APP_PORT}
#RUN chmod +x /fastapi_app/run_celery_and_flower.sh

#ENTRYPOINT ["sh","/fastapi_app/run_celery_and_flower.sh"]
CMD ["python", "main.py"]