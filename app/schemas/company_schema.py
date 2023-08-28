from typing import List
from datetime import datetime
from pydantic import BaseModel


class CompanyCreate(BaseModel):
    name: str
    phone: str
    email: str
    status: bool


class CompanyUpdateInfo(CompanyCreate):
    name: str
    phone: str
    email: str


class CompanyUpdateStatus(BaseModel):
    status: bool


class CompanyResponse(CompanyCreate):
    id: int
    created_at: datetime
    updated_at: datetime


class UserCompanyRole(BaseModel):
    role: str | None = None


class CompanyListResponse(BaseModel):
    companies: List[CompanyResponse]


class CompanyListResponseWithPagination(BaseModel):
    total_item: int
    total_page: int
    data: List[CompanyResponse]

    class Config:
        from_attributes = True


class MyCompanyResponse(BaseModel):
    id: int
    name: str
    phone: str
    email: str
    status: bool
    role: str
    employee_id: int


class MyCompaniesListResponseWithPagination(BaseModel):
    total_item: int
    total_page: int
    data: List[MyCompanyResponse]

    class Config:
        from_attributes = True


class CompanyResponseWithEmployee(BaseModel):
    id: int
    name: str
    phone: str
    email: str
    status: bool
    created_at: datetime
    updated_at: datetime

    employee_id: int
    role: str
    request_status: str | None = None
    invitation_status: str | None = None


class CompaniesListResponseWithEmployeeWithPagination(BaseModel):
    total_item: int
    total_page: int
    data: List[CompanyResponseWithEmployee]

    class Config:
        from_attributes = True
