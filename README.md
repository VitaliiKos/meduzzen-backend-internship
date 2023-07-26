## To run an application in a Docker environment, follow these steps:

1. Install Docker on your system if it is not already installed. Instructions for installing Docker can be found on the official Docker website (https://www.docker.com/).

2. Make sure you have the Dockerfile, docker-compose.yml, and nginx.conf files in your project.

3. Open a terminal or command prompt and navigate to the root directory of the project where the docker-compose.yml file is located.

4 Run the following command to build and run the container:

### docker-compose up

This command will build and run containers according to the settings in the docker-compose.yml file.

After successful launch, you can access the application using your web browser by going to:
### http://localhost.


## Database migrations

To create and apply database migrations, we use Alembic.

1. Initialize the migrations:
   ```
   alembic init -t async migrations
   ```

2. Create automatic migrations based on changes in SQLAlchemy models:
   ```
   alembic revision --autogenerate -m "init"
   ```

3. Apply the migrations to the database:
   ```
   alembic upgrade head
   ```