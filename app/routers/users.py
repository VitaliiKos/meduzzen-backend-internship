from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.exc import IntegrityError
from db.database import get_session
import logging

from schemas.schemas import User, UserCreate, UserUpdate, UsersListResponse, UserUpdateRequest, UserResponse
from models.models import User as UserModel
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.get("/", response_model=UsersListResponse)
async def get_users(skip: int = 0, limit: int = 10, session=Depends(get_session)):
    logger.info("Get all users.")
    users = await session.execute(UserModel.__table__.select().offset(skip).limit(limit))
    return {"users": users}


@router.get("/{user_id}", response_model=User)
async def get_user(user_id: int, session=Depends(get_session)):
    logger.info(f"Get user by id ID: {user_id}.")
    user = await session.get(UserModel, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=User)
async def create_user(user_data: UserCreate, session=Depends(get_session)):
    logger.info("Creating a new user...")
    password_hash = pwd_context.hash(user_data.password)
    user_data.password = password_hash
    user = UserModel(**user_data.model_dump())
    try:
        session.add(user)
        await session.commit()
        await session.refresh(user)
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail="User with this email already exists")
    return user


@router.put("/{user_id}", response_model=UserUpdateRequest)
async def update_user(user_id: int, user_data: UserUpdate, session=Depends(get_session)):
    logger.info(f"Updating user with ID: {user_id}.")
    user = await session.get(UserModel, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    for field, value in user_data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)

    await session.commit()
    await session.refresh(user)
    return user


@router.delete("/{user_id}", response_model=User)
async def delete_user(user_id: int, session=Depends(get_session)):
    logger.info(f"Deleting user with ID: {user_id}.")
    user = await session.get(UserModel, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    await session.delete(user)
    await session.commit()
    return user
