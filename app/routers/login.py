from fastapi import HTTPException, APIRouter, Depends

from schemas.auth import UserAuth, SignInRequest, UserAuthCreate, UserAuthResponseBase
from schemas.token import Token
from schemas.user import UserResponse, User
from fastapi.security import HTTPBearer
from services.user_service import UserService

router = APIRouter()
auth_token_schemas = HTTPBearer()


@router.post("/sign-in", response_model=Token)
async def sign_in(request: SignInRequest, service: UserService = Depends()) -> Token:
    token = await service.authenticate_user(request.email, request.password)
    if token is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return token


@router.post("/sign-up", response_model=UserAuth)
async def sign_up(user_data: UserAuthCreate, service: UserService = Depends()) -> UserAuthResponseBase:
    user = await service.register_user(user_data)
    return user


@router.get("/ath_me", response_model=UserResponse)
async def login_auth0(token=Depends(auth_token_schemas), service: UserService = Depends()) -> User:
    user = await service.get_me_from_auth(token)
    return user
