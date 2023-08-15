import logging
import math

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, Depends, status
from db.database import get_session
from sqlalchemy.exc import IntegrityError

from models.models import Company as CompanyModel, Company
from models.models import Employee as EmployeeModel
from schemas.company_schema import CompanyListResponseWithPagination, CompanyResponse, \
    CompanyCreate, CompanyUpdateInfo, UserCompanyRole
from schemas.employee import EmployeeCreate, Employee

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CompanyService:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session

    async def get_all_companies(self, skip: int, limit: int) -> CompanyListResponseWithPagination:
        logger.info("Get all companies.")

        # companies = select(CompanyModel).where(CompanyModel.__table__.c.status == True)
        # all_companies = await self.session.scalar(companies)

        companies = await self.session.execute(
            CompanyModel.__table__.select().where(CompanyModel.__table__.c.status == True).offset(skip).limit(limit))
        all_companies = companies.fetchall()
        companies_list = []

        for company in all_companies:
            companies_list.append(CompanyResponse(
                id=company.id,
                name=company.name,
                email=company.email,
                phone=company.phone,
                status=company.status,
                created_at=company.created_at,
                updated_at=company.updated_at
            ))

        items = await self.session.execute(
            CompanyModel.__table__.select().where(CompanyModel.__table__.c.status == True))
        total_item = len(items.all())
        total_page = math.ceil(math.ceil(total_item / limit))

        return CompanyListResponseWithPagination(data=companies_list, total_item=total_item,
                                                 total_page=total_page)

    async def get_company_by_id(self, company_id: int) -> CompanyResponse:
        company: CompanyResponse | None = await self.session.get(CompanyModel, company_id)
        if company is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        logger.info(f"Get company by id: {company_id}.")

        return company

    async def create_company(self, current_user_id: int, company_data: CompanyCreate) -> Company:
        company = CompanyModel(**company_data.model_dump())

        try:
            self.session.add(company)
            await self.session.commit()
            await self.session.refresh(company)
            await self.create_employee(user_id=current_user_id, company_id=company.id, role='Owner')
        except IntegrityError as e:
            await self.session.rollback()
            logger.error(f"Error creating company: {e}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Company with this name already exists")
        logger.info("Creating a new company...")
        return company
        # return CompanyResponse(company=company)

    async def update_company(self, company_id: int, company_data: CompanyUpdateInfo,
                             current_user_id: int) -> CompanyResponse:
        await self.check_company_owner(user_id=current_user_id, company_id=company_id)

        company = await self.get_company_by_id(company_id=company_id)
        try:

            for field, value in company_data.model_dump(exclude_unset=True).items():
                setattr(company, field, value)
            await self.session.commit()
            await self.session.refresh(company)
            logger.info(f"Updating company with ID: {company_id}.")
            return company

        except IntegrityError as e:
            logger.error(f"Error updating company: {e}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Company with this name already exists")

    async def update_company_status(self, company_id: int, current_user_id: int) -> CompanyResponse:
        await self.check_company_owner(user_id=current_user_id, company_id=company_id)

        company = await self.get_company_by_id(company_id=company_id)
        try:
            company.status = not company.status
            await self.session.commit()
            await self.session.refresh(company)
            logger.info(f"Updating company status with ID: {company_id}.")
            return company

        except IntegrityError as e:
            logger.error(f"Error updating company status: {e}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Company with this name already exists")

    async def delete_company(self, company_id: int, current_user_id: int) -> None:
        await self.check_company_owner(user_id=current_user_id, company_id=company_id)
        try:
            company = await self.get_company_by_id(company_id)

            employees = await self.session.execute(
                select(EmployeeModel).where(EmployeeModel.company_id == company_id)
            )

            for employee in employees.scalars():
                await self.session.delete(employee)

            await self.session.delete(company)

            await self.session.commit()

        except Exception as e:
            await self.session.rollback()
            raise e

    async def create_employee(self, user_id: int, company_id: int, role: str) -> None:

        employee_data = EmployeeCreate(
            user_id=user_id,
            company_id=company_id,
            role=role
        )

        employee = EmployeeModel(**employee_data.model_dump())

        self.session.add(employee)
        await self.session.commit()
        await self.session.refresh(employee)
        logger.info("Creating a new company...")

    async def check_company_owner(self, user_id: int, company_id: int) -> None:
        query = select(EmployeeModel).where(EmployeeModel.user_id == user_id, EmployeeModel.company_id == company_id)
        employee = await self.session.scalar(query)

        if not employee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You don't have permission!")

    async def check_company_role(self, user_id: int, company_id: int) -> Employee:
        query = select(EmployeeModel).where(EmployeeModel.user_id == user_id, EmployeeModel.company_id == company_id)
        employee = await self.session.scalar(query)

        return employee

    async def get_my_companies(self, skip: int, limit: int, current_user_id: int) -> CompanyListResponseWithPagination:
        logger.info("Get my companies.")
        user_companies = await self.session.execute(
            select(CompanyModel)
            .join(EmployeeModel, CompanyModel.id == EmployeeModel.company_id)
            .where(EmployeeModel.user_id == current_user_id).offset(skip).limit(limit)
        )

        companies_list = []

        for company in user_companies.scalars():
            companies_list.append(CompanyResponse(
                id=company.id,
                name=company.name,
                email=company.email,
                phone=company.phone,
                status=company.status,
                created_at=company.created_at,
                updated_at=company.updated_at
            ))

        items = await self.session.execute(
            select(CompanyModel)
            .join(EmployeeModel, CompanyModel.id == EmployeeModel.company_id)
            .where(EmployeeModel.user_id == current_user_id)
        )
        total_item = len(items.fetchall())

        total_page = math.ceil(math.ceil(total_item / limit))

        return CompanyListResponseWithPagination(data=companies_list, total_item=total_item,

                                                 total_page=total_page)

    async def get_company_by_id_with_role(self, company_id: int, current_user_id: int) -> UserCompanyRole:

        employee = await self.check_company_role(user_id=current_user_id, company_id=company_id)

        if not employee:
            return UserCompanyRole(role='Guest')

        return UserCompanyRole(role=employee.role)
