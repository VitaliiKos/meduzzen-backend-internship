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


class CompanyListResponse(BaseModel):
    companies: List[CompanyResponse]
