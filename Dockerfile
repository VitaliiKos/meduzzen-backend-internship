FROM python:3.11.2-alpine

MAINTAINER Vitalii

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies for PostgreSQL development (if required)
RUN apk update && apk add --no-cache postgresql-dev gcc musl-dev

# Install pipenv
RUN pip install --upgrade pip && pip install pipenv

# Copy the Pipfile and Pipfile.lock into the container
COPY Pipfile Pipfile.lock /app/

# Install project dependencies using pipenv
RUN pipenv install --system --deploy --ignore-pipfile
RUN pip install python-multipart python-dotenv

# Copy the rest of the application files into the container
COPY . .

EXPOSE 8000

CMD ["python", "app/run.py", "--host=0.0.0.0", "--port=8000"]
