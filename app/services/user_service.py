import logging
from fastapi.exceptions import HTTPException, ResponseValidationError
from sqlalchemy.exc import IntegrityError
from models.models import User as UserModel
from schemas.schemas import UserCreate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger(__name__)


class UserService:
    @staticmethod
    async def get_all_users(skip: int, limit: int, session):
        logger.info("Get all users.")
        return await session.execute(UserModel.__table__.select().offset(skip).limit(limit))

    @staticmethod
    async def get_user_by_id(user_id, session):
        user = await session.get(UserModel, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        logger.info(f"Get user by id ID: {user_id}.")
        return user

    @staticmethod
    async def create_user(user_data: UserCreate, session):
        password_hash = pwd_context.hash(user_data.password)
        user_data.password = password_hash
        user = UserModel(**user_data.model_dump())
        try:
            session.add(user)
            await session.commit()
            await session.refresh(user)
        except IntegrityError as e:
            await session.rollback()
            logger.error(f"Error creating user: {e}")
            raise HTTPException(status_code=400, detail="User with this email already exists")
        logger.info("Creating a new user...")
        return user

    @staticmethod
    async def update_user(user_id, user_data, session):

        user = await session.get(UserModel, user_id)
        try:
            if user is None:
                logger.error(f"Error updating user: {user_id}")
                raise HTTPException(status_code=404, detail="User not found")
            for field, value in user_data.model_dump(exclude_unset=True).items():
                setattr(user, field, value)
            await session.commit()
            await session.refresh(user)
            logger.info(f"Updating user with ID: {user_id}.")
            return user

        except IntegrityError as e:
            logger.error(f"Error updating user: {e}")
            raise HTTPException(status_code=400, detail="User with this email already exists")

    @staticmethod
    async def delete_by_id(user_id, session):
        user = await session.get(UserModel, user_id)
        if user is None:
            logger.error(f"Error deleting user: {user_id}")
            raise HTTPException(status_code=404, detail="User not found")

        await session.delete(user)
        await session.commit()
        logger.info(f"Deleting user with ID: {user_id}.")
        return user
