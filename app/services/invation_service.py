import logging
from datetime import datetime

from sqlalchemy import select, and_, or_
from fastapi import HTTPException, status

from models.models import Employee as EmployeeModel, User as UserModel
from schemas.employee import EmployeeRequestResponse, EmployeeInvitationResponse, EmployeeListInvitations, \
    EmployeeListRequest
from schemas.user_schema import UserResponse, UsersListResponse
from services.company_service import CompanyService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InvitationService(CompanyService):

    async def send_invitation_from_company(self, invitation_status: str, company_id: int,
                                           user_id: int) -> EmployeeModel:

        await self.check_company_owner(company_id=company_id)
        await self.check_presence_company(company_id=company_id)
        await self.checking_for_presence_connections_between_user_company(company_id=company_id, user_id=user_id)

        new_employee = EmployeeModel(user_id=user_id, company_id=company_id, role='Candidate')
        new_employee.invitation_status = invitation_status
        new_employee.created_at = datetime.utcnow()
        self.session.add(new_employee)
        await self.session.commit()

        return new_employee

    async def cancel_invitation_request(self, employee_id: int) -> None:
        existing_employee = await self.session.get(EmployeeModel, employee_id)

        await self.check_company_owner(company_id=existing_employee.company_id)

        await self.session.delete(existing_employee)
        await self.session.commit()

    async def accept_invitation(self, employee_id: int, invitation_status: str = 'accept') -> None:
        existing_employee: EmployeeModel | None = await self.session.get(EmployeeModel, employee_id)

        await self.checking_for_presence_connections_between_user_company_for_accept(candidate=existing_employee)

        existing_employee.invitation_status = invitation_status
        existing_employee.created_at = datetime.utcnow()
        existing_employee.role = 'Member'
        await self.session.commit()

    async def send_request(self, invitation_status: str, company_id: int) -> EmployeeModel:

        await self.checking_for_presence_connections_between_user_company(company_id=company_id, user_id=self.user.id)

        new_employee = EmployeeModel(user_id=self.user.id, company_id=company_id, role='Employee')
        new_employee.request_status = invitation_status
        new_employee.created_at = datetime.utcnow()
        self.session.add(new_employee)
        await self.session.commit()

        # new_invitation = EmployeeRequestResponse.model_validate(new_employee, from_attributes=True)
        return new_employee

    async def accept_request(self, invitation_status: str, employee_id: int) -> None:
        existing_employee: EmployeeModel | None = await self.session.get(EmployeeModel, employee_id)

        await self.check_company_owner(company_id=existing_employee.company_id)
        await self.check_is_user_not_member(worker=existing_employee)
        await self.check_candidate_for_request(candidate=existing_employee)

        existing_employee.request_status = invitation_status
        existing_employee.created_at = datetime.utcnow()
        existing_employee.role = 'Member'
        await self.session.commit()

    async def get_user_invitations(self, skip: int, limit: int,
                                   invitation_status: str = None, ) -> EmployeeListInvitations:
        query = await self.session.execute(
            select(EmployeeModel).where(EmployeeModel.__table__.c.user_id == self.user.id,
                                        EmployeeModel.__table__.c.invitation_status == invitation_status).offset(
                skip).limit(limit))
        employee_list = query.scalars().all()

        user_list_invitations = [EmployeeInvitationResponse.model_validate(employee, from_attributes=True) for employee
                                 in
                                 employee_list]

        return EmployeeListInvitations(invitations_list=user_list_invitations)

    async def get_user_requests(self, skip: int, limit: int,
                                request_status: str = None) -> EmployeeListRequest:

        user_requests = await self.session.execute(
            EmployeeModel.__table__.select().where(EmployeeModel.__table__.c.request_status == request_status,
                                                   EmployeeModel.user_id == self.user.id).offset(skip).limit(limit))
        all_requests = user_requests.fetchall()

        user_list_request = [EmployeeRequestResponse.model_validate(employee, from_attributes=True) for employee in
                             all_requests]

        return EmployeeListRequest(request_list=user_list_request)

    async def get_company_requests(self, company_id: int, request_status: str, skip: int,
                                   limit: int) -> EmployeeListRequest:

        await self.check_company_owner(company_id=company_id)

        employees = await self.session.execute(
            EmployeeModel.__table__.select().where(EmployeeModel.__table__.c.company_id == company_id,
                                                   EmployeeModel.__table__.c.request_status == request_status).offset(
                skip).limit(limit))

        all_employees = employees.fetchall()

        user_list_request = [EmployeeRequestResponse.model_validate(employee, from_attributes=True) for employee in
                             all_employees]

        return EmployeeListRequest(request_list=user_list_request)

    async def get_company_invitations(self, company_id: int, invitation_status: str, skip: int,
                                      limit: int) -> EmployeeListInvitations:

        await self.check_company_owner(company_id=company_id)

        employees_invitation = await self.session.execute(
            EmployeeModel.__table__.select().where(EmployeeModel.__table__.c.company_id == company_id,
                                                   EmployeeModel.__table__.c.invitation_status == invitation_status).offset(
                skip).limit(limit))

        all_employees_invitation = employees_invitation.fetchall()

        user_list_request = [EmployeeInvitationResponse.model_validate(employee, from_attributes=True) for employee in
                             all_employees_invitation]

        return EmployeeListInvitations(invitations_list=user_list_request)

    async def get_company_members(self, company_id: int, skip: int, limit: int) -> UsersListResponse:
        await self.check_company_owner(company_id=company_id)

        employees_invitation = await self.session.execute(
            EmployeeModel.__table__.select().where(and_(EmployeeModel.__table__.c.company_id == company_id,
                                                        or_(EmployeeModel.__table__.c.invitation_status == 'accept',
                                                            EmployeeModel.__table__.c.request_status == 'accept'))
                                                   ).offset(skip).limit(limit))

        all_employees_invitation = employees_invitation.fetchall()

        members_list_res = []

        for employee in all_employees_invitation:
            get_user: UserResponse | None = await self.session.get(UserModel, employee.user_id)

            user_request = UserResponse.model_validate(get_user, from_attributes=True)
            members_list_res.append(user_request)

        return UsersListResponse(users=members_list_res)

    async def remove_worker_from_company(self, company_id: int, user_id: int) -> None:

        await self.check_company_owner(company_id=company_id)
        await self.check_user_is_not_owner(user_id=user_id)
        await self.checking_for_presence_connections_between_user_company_for_remove_user(company_id=company_id,
                                                                                          user_id=user_id)

        stmt = select(EmployeeModel).where(EmployeeModel.company_id == company_id,
                                           EmployeeModel.user_id == user_id)
        employees_invitation = await self.session.execute(stmt)

        for employee_invitation in employees_invitation.scalars().all():
            await self.session.delete(employee_invitation)

        await self.session.commit()

    async def leave_company(self, company_id: int) -> None:

        await self.checking_for_presence_connections_between_user_company_for_remove_user(company_id=company_id,
                                                                                          user_id=self.user.id)
        await self.check_is_user_member(company_id=company_id)

        stmt = select(EmployeeModel).where(EmployeeModel.company_id == company_id,
                                           EmployeeModel.user_id == self.user.id)
        employees_invitation = await self.session.execute(stmt)

        for employee_invitation in employees_invitation.scalars().all():
            await self.session.delete(employee_invitation)

        await self.session.commit()

    async def checking_for_presence_connections_between_user_company(self, company_id: int, user_id: int) -> None:
        existing_employee = await self.session.execute(
            select(EmployeeModel).where(EmployeeModel.company_id == company_id,
                                        EmployeeModel.user_id == user_id))

        all_existing = existing_employee.fetchall()

        if all_existing:
            raise HTTPException(status_code=status.HTTP_208_ALREADY_REPORTED,
                                detail="An invitation or request already exists for this user")

    async def checking_for_presence_connections_between_user_company_for_remove_user(self, company_id: int,
                                                                                     user_id: int) -> None:
        existing_employee = await self.session.execute(
            select(EmployeeModel).where(EmployeeModel.company_id == company_id,
                                        EmployeeModel.user_id == user_id))

        all_existing = existing_employee.fetchall()

        if not all_existing:
            raise HTTPException(status_code=status.HTTP_208_ALREADY_REPORTED,
                                detail="Not Found.")

    async def checking_for_presence_connections_between_user_company_for_accept(self, candidate: EmployeeModel) -> None:

        if not candidate or candidate.user_id != self.user.id or not candidate.invitation_status:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="You don't have invitation from this company.")

    async def check_user_is_not_owner(self, user_id: int):
        if user_id == self.user.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="You cannot fire yourself from the company.")

    @staticmethod
    async def check_is_user_not_member(worker: EmployeeModel):
        if worker.role == 'member':
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="This employee already works for your company.")

    async def check_is_user_member(self, company_id: int):
        query = await self.session.execute(
            select(EmployeeModel).where(EmployeeModel.__table__.c.user_id == self.user.id,
                                        EmployeeModel.__table__.c.company_id == company_id))
        employee = query.scalars().first()

        if not employee or employee.role != 'Member':
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Not Found.")

    @staticmethod
    async def check_candidate_for_request(candidate: EmployeeModel):
        if not candidate.request_status:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="This user is not in the list of candidates.")
