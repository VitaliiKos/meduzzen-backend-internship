import logging
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, Depends, status
from db.database import get_session

from models.models import Employee as EmployeeModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InvitationService:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session

    async def send_invitation(self, invitation_status: str, company_id: int, user_id: int):
        existing_employee = await self.session.execute(
            select(EmployeeModel).where(EmployeeModel.company_id == company_id, EmployeeModel.user_id == user_id)
        )
        all_existing = existing_employee.fetchall()
        if all_existing:
            raise HTTPException(status_code=status.HTTP_208_ALREADY_REPORTED,
                                detail="An invitation or request already exists for this user")

        new_employee = EmployeeModel(user_id=user_id, company_id=company_id, role='Employee')
        new_employee.invitation_status = invitation_status
        new_employee.invitation_sent_at = datetime.utcnow()
        self.session.add(new_employee)
        await self.session.commit()

    async def cancel_invitation(self, employee_id: int):
        existing_employee = await self.session.get(EmployeeModel, employee_id)

        existing_employee.invitation_status = None
        existing_employee.invitation_sent_at = None
        await self.session.commit()

    async def accept_invitation(self, invitation_status: str, employee_id: int):
        existing_employee = await self.session.get(EmployeeModel, employee_id)

        existing_employee.invitation_status = invitation_status
        existing_employee.invitation_sent_at = datetime.utcnow()
        existing_employee.role = 'Member'
        await self.session.commit()

    # ******************************************************************
    async def send_request(self, invitation_status: str, company_id: int, user_id: int):
        existing_employee = await self.session.execute(
            select(EmployeeModel).where(EmployeeModel.company_id == company_id))

        all_existing = existing_employee.fetchall()

        if all_existing:
            raise HTTPException(status_code=status.HTTP_208_ALREADY_REPORTED,
                                detail="An invitation or request already exists for this user")

        new_employee = EmployeeModel(user_id=user_id, company_id=company_id, role='Employee')
        new_employee.request_status = invitation_status
        new_employee.request_sent_at = datetime.utcnow()
        self.session.add(new_employee)
        await self.session.commit()

    async def cancel_request(self, employee_id: int):
        existing_employee = await self.session.get(EmployeeModel, employee_id)

        existing_employee.request_status = None
        existing_employee.request_sent_at = None
        await self.session.commit()

    async def accept_request(self, invitation_status: str, employee_id: int):
        existing_employee = await self.session.get(EmployeeModel, employee_id)

        existing_employee.request_status = invitation_status
        existing_employee.request_sent_at = datetime.utcnow()
        existing_employee.role = 'Member'
        await self.session.commit()

    # ******************************************************************
    async def get_user_invitations(self, current_user_id: int, invitation_status: str = None):
        query = await self.session.execute(
            select(EmployeeModel).where(EmployeeModel.__table__.c.user_id == current_user_id,
                                        EmployeeModel.__table__.c.invitation_status == invitation_status)
        )
        employee_list = query.scalars().all()

        return employee_list

    async def get_user_requests(self, current_user_id: int, requests_status: str = None):

        user_requests = await self.session.execute(
            EmployeeModel.__table__.select().where(EmployeeModel.__table__.c.requests_status == requests_status),
            EmployeeModel.user_id == current_user_id)
        all_requests = user_requests.fetchall()

        return all_requests

    # ******************************************************************
    async def get_company_invitations(self, current_user_id: int, company_id: int ):
        query = await self.session.execute(
            select(EmployeeModel).where(EmployeeModel.__table__.c.user_id == current_user_id,
                                        EmployeeModel.__table__.c.company_id == company_id)
        )
        employee_list = query.scalars().all()

        return employee_list

    async def get_company_requests(self, current_user_id: int, company_id: int):
        print('G'*50)
        company_requests = await self.session.execute(
            EmployeeModel.__table__.select().where(EmployeeModel.__table__.c.company_id == company_id),
            EmployeeModel.user_id == current_user_id)
        all_requests = company_requests.fetchall()
        print('H'*50)

        return all_requests

        # company_requests = await self.session.execute(
        #     EmployeeModel.__table__.select().where(EmployeeModel.__table__.c.company_id == company_id),
        #     EmployeeModel.user_id == current_user_id)
        # all_requests = company_requests.fetchall()
        #
        # return all_requests
