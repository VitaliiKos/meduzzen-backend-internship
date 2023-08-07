from pydantic import BaseModel
from datetime import datetime


class UserAuthBase(BaseModel):
    email: str


class UserAuthCreate(UserAuthBase):
    password: str


class UserAuthResponseBase(UserAuthBase):
    id: int
    created_at: datetime
    updated_at: datetime


class UserAuth(UserAuthResponseBase):
    pass


class SignInRequest(BaseModel):
    email: str
    password: str


class SignUpRequest(BaseModel):
    email: str
    password: str
