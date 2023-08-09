from pydantic import BaseModel


class EmployeeCreate(BaseModel):
    user_id: int
    company_id: int
    role: str


class Employee(EmployeeCreate):
    id: int
