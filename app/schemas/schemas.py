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

    class Config:
        from_attributes = True


class UserUpdate(UserBase):
    class Config:
        from_attributes = True


class UserResponseBase(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class User(UserResponseBase):
    pass


class SignInRequest(BaseModel):
    username: str
    password: str


class SignUpRequestBase(BaseModel):
    username: str
    email: str
    password: str


class UserUpdateRequest(UserResponseBase):
    pass


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    phone_number: str = None
    age: int = None
    city: str = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UsersListResponse(BaseModel):
    users: List[UserResponse]

    class Config:
        from_attributes = True
