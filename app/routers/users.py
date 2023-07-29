from fastapi import APIRouter, Depends
from db.database import get_session

from schemas.schemas import User, UserCreate, UserUpdate, UsersListResponse, UserUpdateRequest

from services.user_service import UserService

router = APIRouter()

user_service = UserService()


@router.get("/", response_model=UsersListResponse)
async def get_users(skip: int = 0, limit: int = 10, session=Depends(get_session)):
    return {"users": await user_service.get_all_users(skip, limit, session)}


@router.get("/{user_id}", response_model=User)
async def get_user(user_id: int, session=Depends(get_session)):
    return await user_service.get_user_by_id(user_id, session)


@router.post("/", response_model=User)
async def create_user(user_data: UserCreate, session=Depends(get_session)):
    return await user_service.create_user(user_data, session)


@router.put("/{user_id}", response_model=UserUpdateRequest)
async def update_user(user_id: int, user_data: UserUpdate, session=Depends(get_session)):
    return await user_service.update_user(user_id, user_data, session)


@router.delete("/{user_id}", response_model=User)
async def delete_user(user_id: int, session=Depends(get_session)):
    return await user_service.delete_by_id(user_id, session)
