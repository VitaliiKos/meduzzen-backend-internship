from pydantic import BaseModel
from datetime import datetime
from typing import List


class UserBase(BaseModel):
    email: str
    username: str
    password: str
    phone_number: str = None
    age: int = None
    city: str = None


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    pass


class UserResponseBase(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class User(UserResponseBase):
    pass


class UserResponse(UserResponseBase):
    pass


class SignInRequest(BaseModel):
    username: str
    password: str


class SignUpRequestBase(BaseModel):
    username: str
    email: str
    password: str


class UserUpdateRequest(BaseModel):
    email: str
    password: str


class UsersListResponse(BaseModel):
    users: List[UserResponse]
