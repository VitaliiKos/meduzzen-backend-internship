from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# SQLALCHEMY_DATABASE_URL = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost/{POSTGRES_DB}'
SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://tamtik:root@postgres:5432/root"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True, future=True)
async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
            session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            session.close()


# async def check_redis_connection():
#     pass
    # try:
    #     conn = await asyncio_redis.Connection.create(host='', post=6379)
    #     await conn.close()
    #     return True
    # except Exception as error:
    #     return error
