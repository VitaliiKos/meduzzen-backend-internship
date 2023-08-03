from fastapi import Depends
from db.database import get_session
from schemas.user import User
from services.user_service import UserService
from fastapi.security import HTTPBearer

auth_token_schemas = HTTPBearer()


async def authenticate_and_get_user(token=Depends(auth_token_schemas), session=Depends(get_session)) -> User:
    user_service = UserService(session=session)
    user = await user_service.get_or_create_user_from_token(token)
    return user
