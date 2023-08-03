from fastapi import HTTPException, APIRouter, Depends

from db.database import get_session
from schemas.auth import UserAuth, SignInRequest, UserAuthCreate, UserAuthResponseBase
from schemas.token import Token
from schemas.user import UserResponse, User
from fastapi.security import HTTPBearer
from services.user_service import UserService

router = APIRouter()
auth_token_schemas = HTTPBearer()


@router.post("/sign-in", response_model=Token)
async def sign_in(request: SignInRequest, session=Depends(get_session)) -> Token:
    user_service = UserService(session=session)
    token = await user_service.authenticate_user(request.email, request.password)
    if token is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return token


@router.post("/sign-up", response_model=UserAuth)
async def sign_up(user_data: UserAuthCreate, session=Depends(get_session)) -> UserAuthResponseBase:
    user_service = UserService(session=session)
    user = await user_service.register_user(user_data=user_data)
    return user


@router.get("/me", response_model=UserResponse)
async def login_auth0(token=Depends(auth_token_schemas), session=Depends(get_session)) -> User:
    user_service = UserService(session=session)
    user = await user_service.get_current_user(token)
    return user
