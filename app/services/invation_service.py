import logging
from datetime import datetime

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, Depends, status
from db.database import get_session

from models.models import Employee as EmployeeModel, User as UserModel
from schemas.employee import EmployeeRequestResponse, EmployeeInvitationResponse, EmployeeListInvitations, \
    EmployeeListRequest
from schemas.user_schema import UserResponse, UsersListResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InvitationService:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session

    async def send_invitation(self, invitation_status: str, company_id: int,
                              user_id: int) -> EmployeeInvitationResponse:
        existing_employee = await self.session.execute(
            select(EmployeeModel).where(EmployeeModel.company_id == company_id, EmployeeModel.user_id == user_id)
        )
        all_existing = existing_employee.fetchall()
        if all_existing:
            raise HTTPException(status_code=status.HTTP_208_ALREADY_REPORTED,
                                detail="An invitation or request already exists for this user")

        new_employee = EmployeeModel(user_id=user_id, company_id=company_id, role='Candidate')
        new_employee.invitation_status = invitation_status
        new_employee.created_at = datetime.utcnow()
        self.session.add(new_employee)
        await self.session.commit()

        new_candidate = EmployeeInvitationResponse.model_validate(new_employee, from_attributes=True)
        return new_candidate

    async def cancel_invitation_request(self, employee_id: int) -> None:
        existing_employee = await self.session.get(EmployeeModel, employee_id)
        await self.session.delete(existing_employee)
        await self.session.commit()

    async def accept_invitation(self, invitation_status: str, employee_id: int) -> None:
        existing_employee = await self.session.get(EmployeeModel, employee_id)

        existing_employee.invitation_status = invitation_status
        existing_employee.created_at = datetime.utcnow()
        existing_employee.role = 'Member'
        await self.session.commit()

    async def send_request(self, invitation_status: str, company_id: int, user_id: int) -> EmployeeRequestResponse:
        existing_employee = await self.session.execute(
            select(EmployeeModel).where(EmployeeModel.company_id == company_id, EmployeeModel.user_id == user_id))

        all_existing = existing_employee.fetchall()

        if all_existing:
            raise HTTPException(status_code=status.HTTP_208_ALREADY_REPORTED,
                                detail="An invitation or request already exists for this user")

        new_employee = EmployeeModel(user_id=user_id, company_id=company_id, role='Employee')
        new_employee.request_status = invitation_status
        new_employee.created_at = datetime.utcnow()
        self.session.add(new_employee)
        await self.session.commit()

        new_invitation = EmployeeRequestResponse.model_validate(new_employee, from_attributes=True)
        return new_invitation

    async def accept_request(self, invitation_status: str, employee_id: int) -> None:
        existing_employee = await self.session.get(EmployeeModel, employee_id)

        existing_employee.request_status = invitation_status
        existing_employee.created_at = datetime.utcnow()
        existing_employee.role = 'Member'
        await self.session.commit()

    async def get_user_invitations(self, current_user_id: int,
                                   invitation_status: str = None) -> EmployeeListInvitations:
        query = await self.session.execute(
            select(EmployeeModel).where(EmployeeModel.__table__.c.user_id == current_user_id,
                                        EmployeeModel.__table__.c.invitation_status == invitation_status)
        )
        employee_list = query.scalars().all()

        user_list_invitations = [EmployeeInvitationResponse.model_validate(employee, from_attributes=True) for employee
                                 in
                                 employee_list]

        return EmployeeListInvitations(invitations_list=user_list_invitations)

    async def get_user_requests(self, current_user_id: int, request_status: str = None) -> EmployeeListRequest:

        user_requests = await self.session.execute(
            EmployeeModel.__table__.select().where(EmployeeModel.__table__.c.request_status == request_status,
                                                   EmployeeModel.user_id == current_user_id))
        all_requests = user_requests.fetchall()

        user_list_request = [EmployeeRequestResponse.model_validate(employee, from_attributes=True) for employee in
                             all_requests]

        return EmployeeListRequest(request_list=user_list_request)

    async def get_company_requests(self, current_user_id: int, company_id: int,
                                   request_status: str) -> EmployeeListRequest:

        employees = await self.session.execute(
            EmployeeModel.__table__.select().where(EmployeeModel.__table__.c.company_id == company_id,
                                                   EmployeeModel.__table__.c.request_status == request_status))

        all_employees = employees.fetchall()

        user_list_request = [EmployeeRequestResponse.model_validate(employee, from_attributes=True) for employee in
                             all_employees]

        return EmployeeListRequest(request_list=user_list_request)

    async def get_company_invitations(self, current_user_id: int, company_id: int,
                                      invitation_status: str) -> EmployeeListInvitations:
        employees_invitation = await self.session.execute(
            EmployeeModel.__table__.select().where(EmployeeModel.__table__.c.company_id == company_id,
                                                   EmployeeModel.__table__.c.invitation_status == invitation_status))

        all_employees_invitation = employees_invitation.fetchall()

        user_list_request = [EmployeeInvitationResponse.model_validate(employee, from_attributes=True) for employee in
                             all_employees_invitation]

        return EmployeeListInvitations(invitations_list=user_list_request)

    async def get_company_members(self, current_user_id: int, company_id: int) -> UsersListResponse:
        employees_invitation = await self.session.execute(
            EmployeeModel.__table__.select().where(and_(EmployeeModel.__table__.c.company_id == company_id,
                                                        or_(EmployeeModel.__table__.c.invitation_status == 'accept',
                                                            EmployeeModel.__table__.c.request_status == 'accept'))
                                                   ))

        all_employees_invitation = employees_invitation.fetchall()

        members_list_res = []

        for employee in all_employees_invitation:
            get_user: UserResponse | None = await self.session.get(UserModel, employee.user_id)

            user_request = UserResponse.model_validate(get_user, from_attributes=True)
            members_list_res.append(user_request)

        return UsersListResponse(users=members_list_res)
