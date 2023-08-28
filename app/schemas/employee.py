from typing import List
from datetime import datetime

from pydantic import BaseModel

from schemas.user_schema import UserResponse


class EmployeeCreate(BaseModel):
    user_id: int
    company_id: int
    role: str


class Employee(EmployeeCreate):
    id: int


class EmployeeRequestResponse(BaseModel):
    id: int
    user_id: int
    company_id: int
    role: str
    request_status: str
    created_at: datetime


class EmployeeInvitationResponse(BaseModel):
    id: int
    user_id: int
    company_id: int
    role: str
    invitation_status: str
    created_at: datetime


class EmployeeListInvitations(BaseModel):
    invitations_list: List[EmployeeInvitationResponse]


class EmployeeListRequest(BaseModel):
    request_list: List[EmployeeRequestResponse]


class Member(BaseModel):
    user: UserResponse
    role: str


class InvitationsListResponseWithPagination(BaseModel):
    total_item: int
    total_page: int
    data: List[EmployeeInvitationResponse]

    class Config:
        from_attributes = True


class RequestsListResponseWithPagination(BaseModel):
    total_item: int
    total_page: int
    data: List[EmployeeRequestResponse]

    class Config:
        from_attributes = True
