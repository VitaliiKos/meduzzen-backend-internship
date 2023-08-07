from fastapi import APIRouter, Depends, status
from starlette.responses import Response

from db.database import get_session

from schemas.user import User, UserCreate, UserUpdate, UsersListResponse, UserResponse
from services.auth import authenticate_and_get_user

from services.user_service import UserService

router = APIRouter()


@router.get("/", response_model=UsersListResponse)
async def get_users(skip: int = 0, limit: int = 10, session=Depends(get_session)) -> UsersListResponse:
    user_service = UserService(session=session)
    users = await user_service.get_all_users(skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=User)
async def get_user(user_id: int, session=Depends(get_session)) -> UserResponse:
    user_service = UserService(session=session)
    user = await user_service.get_user_by_id(user_id=user_id)
    return user


@router.post("/", response_model=User)
async def create_user(user_data: UserCreate, session=Depends(get_session)) -> User:
    user_service = UserService(session=session)
    user = await user_service.create_user(user_data=user_data)
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_data: UserUpdate, current_user=Depends(authenticate_and_get_user),
                      service: UserService = Depends()) -> UserResponse:
    user = await service.update_user(user_id=user_id, user_data=user_data, current_user_id=current_user.id)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, current_user=Depends(authenticate_and_get_user),
                      service: UserService = Depends()) -> Response:
    await service.delete_user(user_id=user_id, current_user_id=current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
