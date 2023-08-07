from fastapi import Depends
from models.models import User
from services.user_service import UserService
from fastapi.security import HTTPBearer

auth_token_schemas = HTTPBearer()


async def authenticate_and_get_user(token=Depends(auth_token_schemas), service: UserService = Depends()) -> User:
    user = await service.get_or_create_user_from_token(token)
    return user
