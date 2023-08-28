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


class UserUpdate(BaseModel):
    username: str
    phone_number: str = None
    age: int = None
    city: str = None


class UserUpdatePassword(BaseModel):
    password: str


class UserResponseBase(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime


class User(UserResponseBase):
    pass


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


class UsersListResponseWithPagination(BaseModel):
    total_item: int
    total_page: int
    data: List[UserResponse]

    class Config:
        from_attributes = True


class MemberResponse(BaseModel):
    id: int
    email: str
    username: str | None = None
    phone_number: str | None = None
    age: int | None = None
    city: str | None = None
    created_at: datetime
    updated_at: datetime
    role: str
    employee_id: int
    request_status: str | None = None
    invitation_status: str | None = None


class MembersListResponseWithPagination(BaseModel):
    total_item: int
    total_page: int
    data: List[MemberResponse]

    class Config:
        from_attributes = True
