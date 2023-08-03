from pydantic import BaseModel
from datetime import datetime
from typing import List


class UserBase(BaseModel):
    email: str
    username: str
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


class User(UserResponseBase):
    pass


class UserUpdateRequest(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    username: str | None = None
    phone_number: str | None = None
    age: int | None = None
    city: str | None = None
    created_at: datetime
    updated_at: datetime


class UsersListResponse(BaseModel):
    users: List[UserResponse]

    class Config:
        from_attributes = True
