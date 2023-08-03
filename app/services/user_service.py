import logging
from typing import Type
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError

from core.token_verify import VerifyToken
from db.database import get_session
from models.models import User as UserModel
from core.hashing import Hasher
from schemas.auth import UserAuthCreate
from schemas.user import UserCreate, UsersListResponse, User, UserResponse
from services.jwt_service import create_jwt_token, decode_jwt_token, check_jwt_type
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session

    async def get_all_users(self, skip: int, limit: int) -> UsersListResponse:
        logger.info("Get all users.")
        users = await self.session.execute(UserModel.__table__.select().offset(skip).limit(limit))
        all_users = users.fetchall()

        users_list = []

        for user in all_users:
            users_list.append(UserResponse(
                id=user.id,
                email=user.email,
                username=user.username,
                phone_number=user.phone_number,
                age=user.age,
                city=user.city,
                created_at=user.created_at,
                updated_at=user.updated_at
            ))

        return UsersListResponse(users=users_list)

    async def get_user_by_id(self, user_id: int) -> Type[User]:
        user = await self.session.get(UserModel, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        logger.info(f"Get user by id ID: {user_id}.")

        return user

    async def create_user(self, user_data: UserCreate) -> User:
        password_hash = Hasher.get_password_hash(user_data.password)
        user_data.password = password_hash
        user = UserModel(**user_data.model_dump())
        try:
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
        except IntegrityError as e:
            await self.session.rollback()
            logger.error(f"Error creating user: {e}")
            raise HTTPException(status_code=400, detail="User with this email already exists")
        logger.info("Creating a new user...")
        return user

    async def update_user(self, user_id, user_data) -> Type[User]:

        user = await self.session.get(UserModel, user_id)
        try:
            if user is None:
                logger.error(f"Error updating user: {user_id}")
                raise HTTPException(status_code=404, detail="User not found")
            for field, value in user_data.model_dump(exclude_unset=True).items():
                setattr(user, field, value)
            await self.session.commit()
            await self.session.refresh(user)
            logger.info(f"Updating user with ID: {user_id}.")
            return user

        except IntegrityError as e:
            logger.error(f"Error updating user: {e}")
            raise HTTPException(status_code=400, detail="User with this email already exists")

    async def delete_by_id(self, user_id) -> Type[User]:
        user = await self.session.get(UserModel, user_id)
        if user is None:
            logger.error(f"Error deleting user: {user_id}")
            raise HTTPException(status_code=404, detail="User not found")

        await self.session.delete(user)
        await self.session.commit()
        logger.info(f"Deleting user with ID: {user_id}.")
        return user

    async def authenticate_user(self, email: str, password: str):

        user = await self.session.execute(UserModel.__table__.select().where(UserModel.email == email))
        user = user.first()
        status_verify_password = Hasher.verify_password(password, user.password)

        if user is None or not status_verify_password:
            return None
        access_token = create_jwt_token(data={"sub": str(user.id), "usr": user.email, "owner": settings.owner})
        return {"access_token": access_token, "token_type": "Bearer"}

    async def register_user(self, user_data: UserAuthCreate) -> UserModel:
        user_data.password = Hasher.get_password_hash(user_data.password)
        user = UserModel(**user_data.model_dump())
        try:
            self.session.add(user)
            await self.session.commit()
            # await self.session.refresh(user)
        except IntegrityError as e:
            await self.session.rollback()
            logger.error(f"Error register user: {e}")
            raise HTTPException(status_code=400, detail="User with this email already exists")
        logger.info("Registering a new user...")
        return user

    async def get_me(self, token) -> User:
        token = token.credentials
        payload = decode_jwt_token(token)
        user_email = payload.get('usr')
        user = await self.get_user_by_email(user_email)
        return user

    async def get_user_by_email(self, email: str) -> User:
        query = select(UserModel).where(UserModel.email == email)
        user = await self.session.scalar(query)

        return user

    async def get_me_from_auth(self, token) -> User:

        current_email = await self.get_email_from_token(token)
        user = await self.get_user_by_email(current_email)
        if not user:
            user_data = UserAuthCreate(email=current_email, password=str(datetime.utcnow))
            user = await self.register_user(user_data)

        return user

    @staticmethod
    async def get_email_from_token(token) -> str:
        check_owner_jwt_type = check_jwt_type(token)

        if check_owner_jwt_type:
            payload = decode_jwt_token(token.credentials)
            email = payload.get('usr')
        else:
            payload = VerifyToken(token.credentials).verify()
            email = payload.get('user_email')

        return email
