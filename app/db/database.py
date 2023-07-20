import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
import databases

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


# SQLALCHEMY_DATABASE_URL = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost/{POSTGRES_DB}'
SQLALCHEMY_DATABASE_URL = "postgresql://tamtik:root@postgres/postgres"
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True, future=True)
asyncSession = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


database = databases.Database(SQLALCHEMY_DATABASE_URL)
metadata = sqlalchemy.MetaData()

metadata.create_all(engine)

Base = declarative_base()
