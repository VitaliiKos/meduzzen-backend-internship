import logging
import math
from datetime import datetime

from sqlalchemy import select
from fastapi import HTTPException, status

from models.models import Employee as EmployeeModel, User as UserModel, Company as CompanyModel
from schemas.company_schema import CompanyListResponseWithPagination, CompanyResponse, CompanyResponseWithEmployee, \
    CompaniesListResponseWithEmployeeWithPagination
from schemas.user_schema import UserResponse, UsersListResponseWithPagination, MemberResponse, \
    MembersListResponseWithPagination
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
        try:
            existing_employee: EmployeeModel | None = await self.session.get(EmployeeModel, employee_id)
            await self.check_candidate_for_request(candidate=existing_employee)

            # await self.check_company_owner(company_id=existing_employee.company_id)

            await self.session.delete(existing_employee)
            await self.session.commit()
        except Exception as error:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="BAD REQUEST.")
    async def accept_invitation(self, employee_id: int, invitation_status: str = 'accept') -> None:
        existing_employee: EmployeeModel | None = await self.session.get(EmployeeModel, employee_id)

        await self.checking_for_presence_connections_between_user_company_for_accept(candidate=existing_employee)

        existing_employee.invitation_status = invitation_status
        existing_employee.created_at = datetime.utcnow()
        existing_employee.role = 'Member'
        await self.session.commit()

    async def reject_invitation(self, employee_id: int) -> None:
        existing_employee: EmployeeModel | None = await self.session.get(EmployeeModel, employee_id)

        await self.checking_for_presence_connections_between_user_company_for_accept(candidate=existing_employee)

        existing_employee.invitation_status = 'Reject'
        existing_employee.created_at = datetime.utcnow()
        await self.session.commit()

    async def send_request(self, invitation_status: str, company_id: int) -> EmployeeModel:

        await self.checking_for_presence_connections_between_user_company(company_id=company_id, user_id=self.user.id)

        new_employee = EmployeeModel(user_id=self.user.id, company_id=company_id, role='Candidate')
        new_employee.request_status = invitation_status
        new_employee.created_at = datetime.utcnow()
        self.session.add(new_employee)
        await self.session.commit()

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

    async def reject_request(self, employee_id: int) -> None:
        existing_employee: EmployeeModel | None = await self.session.get(EmployeeModel, employee_id)
        await self.check_company_owner(company_id=existing_employee.company_id)
        await self.check_candidate_for_request(candidate=existing_employee)

        existing_employee.request_status = 'Reject'
        existing_employee.created_at = datetime.utcnow()
        await self.session.commit()

    async def get_user_invitations(self, skip: int, limit: int,
                                   invitation_status: str = None, ) -> CompaniesListResponseWithEmployeeWithPagination:
        employees_invitation = select(CompanyModel, EmployeeModel.role, EmployeeModel.id,
                                      EmployeeModel.invitation_status,
                                      EmployeeModel.request_status).join(EmployeeModel,
                                                                         EmployeeModel.user_id == self.user.id).where(
            CompanyModel.id == EmployeeModel.company_id,
            EmployeeModel.__table__.c.invitation_status == invitation_status,
            EmployeeModel.__table__.c.role == 'Candidate').offset(skip).limit(limit).order_by('id')

        all_employees_invitation = (await self.session.execute(employees_invitation)).all()

        companies_list = [
            CompanyResponseWithEmployee(
                id=company.id,
                name=company.name,
                phone=company.phone,
                email=company.email,
                status=company.status,
                created_at=company.created_at,
                updated_at=company.updated_at,
                role=role,
                employee_id=employee_id,
                request_status=request_status,
                invitation_status=invitation_status

            )
            for company, role, employee_id, invitation_status, request_status in all_employees_invitation
        ]

        result2_for_pagination = await self.session.execute(
            select(CompanyModel, EmployeeModel.role, EmployeeModel.id, EmployeeModel.invitation_status,
                   EmployeeModel.request_status).join(EmployeeModel, EmployeeModel.user_id == self.user.id).where(
                CompanyModel.id == EmployeeModel.company_id,
                EmployeeModel.__table__.c.invitation_status == invitation_status,
                EmployeeModel.__table__.c.role == 'Candidate'))

        total_item = len(result2_for_pagination.all())
        total_page = math.ceil(math.ceil(total_item / limit))

        return CompaniesListResponseWithEmployeeWithPagination(data=companies_list, total_item=total_item,
                                                               total_page=total_page)

    async def get_user_requests(self, skip: int, limit: int,
                                request_status: str = None) -> CompaniesListResponseWithEmployeeWithPagination:

        employees_requests = select(CompanyModel, EmployeeModel.role, EmployeeModel.id,
                                    EmployeeModel.invitation_status, EmployeeModel.request_status).join(EmployeeModel,
                                                                                                        EmployeeModel.user_id == self.user.id).where(
            CompanyModel.id == EmployeeModel.company_id, EmployeeModel.__table__.c.request_status == request_status,
            EmployeeModel.__table__.c.role == 'Candidate').offset(skip).limit(limit).order_by('id')

        all_employees_invitation = (await self.session.execute(employees_requests)).all()

        companies_list = [
            CompanyResponseWithEmployee(
                id=company.id,
                name=company.name,
                phone=company.phone,
                email=company.email,
                status=company.status,
                created_at=company.created_at,
                updated_at=company.updated_at,
                role=role,
                employee_id=employee_id,
                request_status=request_status,
                invitation_status=invitation_status

            )
            for company, role, employee_id, invitation_status, request_status in all_employees_invitation
        ]

        result2_for_pagination = await self.session.execute(
            select(CompanyModel, EmployeeModel.role, EmployeeModel.id, EmployeeModel.invitation_status,
                   EmployeeModel.request_status).join(EmployeeModel, EmployeeModel.user_id == self.user.id).where(
                CompanyModel.id == EmployeeModel.company_id, EmployeeModel.__table__.c.request_status == request_status,
                EmployeeModel.__table__.c.role == 'Candidate'))

        total_item = len(result2_for_pagination.all())
        total_page = math.ceil(math.ceil(total_item / limit))

        return CompaniesListResponseWithEmployeeWithPagination(data=companies_list, total_item=total_item,
                                                               total_page=total_page)

    async def get_company_requests(self, company_id: int, request_status: str, skip: int,
                                   limit: int) -> MembersListResponseWithPagination:

        await self.check_company_owner(company_id=company_id)

        employees_invitation = select(UserModel, EmployeeModel.role, EmployeeModel.id, EmployeeModel.invitation_status,
                                      EmployeeModel.request_status).join(EmployeeModel,
                                                                         EmployeeModel.company_id == company_id).where(
            UserModel.id == EmployeeModel.user_id, EmployeeModel.__table__.c.request_status == request_status).offset(
            skip).limit(limit).order_by('id')

        all_employees_invitation = (await self.session.execute(employees_invitation)).all()

        user_list = [
            MemberResponse(
                id=user.id,
                email=user.email,
                username=user.username,
                phone_number=user.phone_number,
                age=user.age,
                city=user.city,
                created_at=user.created_at,
                updated_at=user.updated_at,
                role=role,
                employee_id=employee_id,
                request_status=request_status,
                invitation_status=invitation_status

            )
            for user, role, employee_id, invitation_status, request_status in all_employees_invitation
        ]
        result2_for_pagination = await self.session.execute(
            select(UserModel, EmployeeModel.role, EmployeeModel.id, EmployeeModel.invitation_status,
                   EmployeeModel.request_status).join(EmployeeModel, EmployeeModel.company_id == company_id).where(
                UserModel.id == EmployeeModel.user_id, EmployeeModel.__table__.c.request_status == request_status))
        total_item = len(result2_for_pagination.all())
        total_page = math.ceil(math.ceil(total_item / limit))

        return MembersListResponseWithPagination(data=user_list, total_item=total_item, total_page=total_page)

    async def get_company_invitations(self, company_id: int, invitation_status: str, skip: int,
                                      limit: int) -> MembersListResponseWithPagination:

        await self.check_company_owner(company_id=company_id)

        employees_invitation = select(UserModel, EmployeeModel.role, EmployeeModel.id, EmployeeModel.invitation_status,
                                      EmployeeModel.request_status).join(EmployeeModel,
                                                                         EmployeeModel.company_id == company_id).where(
            UserModel.id == EmployeeModel.user_id,
            EmployeeModel.__table__.c.invitation_status == invitation_status).offset(skip).limit(limit).order_by('id')

        all_employees_invitation = (await self.session.execute(employees_invitation)).all()

        user_list = [
            MemberResponse(
                id=user.id,
                email=user.email,
                username=user.username,
                phone_number=user.phone_number,
                age=user.age,
                city=user.city,
                created_at=user.created_at,
                updated_at=user.updated_at,
                role=role,
                employee_id=employee_id,
                request_status=request_status,
                invitation_status=invitation_status

            )
            for user, role, employee_id, invitation_status, request_status in all_employees_invitation
        ]
        result2_for_pagination = await self.session.execute(
            select(UserModel, EmployeeModel.role, EmployeeModel.id, EmployeeModel.invitation_status,
                   EmployeeModel.request_status).join(EmployeeModel, EmployeeModel.company_id == company_id).where(
                UserModel.id == EmployeeModel.user_id,
                EmployeeModel.__table__.c.invitation_status == invitation_status))
        total_item = len(result2_for_pagination.all())
        total_page = math.ceil(math.ceil(total_item / limit))
        return MembersListResponseWithPagination(data=user_list, total_item=total_item, total_page=total_page)

    async def get_company_members(self, company_id: int, skip: int, limit: int):
        await self.check_company_owner(company_id=company_id)

        user_query = select(UserModel, EmployeeModel.role, EmployeeModel.id, EmployeeModel.invitation_status,
                            EmployeeModel.request_status).join(EmployeeModel,
                                                               EmployeeModel.company_id == company_id).where(
            UserModel.id == EmployeeModel.user_id, EmployeeModel.__table__.c.role != 'Candidate').offset(skip).limit(
            limit).order_by('id')
        members = (await self.session.execute(user_query)).all()

        user_list = [
            MemberResponse(
                id=user.id,
                email=user.email,
                username=user.username,
                phone_number=user.phone_number,
                age=user.age,
                city=user.city,
                created_at=user.created_at,
                updated_at=user.updated_at,
                role=role,
                employee_id=employee_id,
                request_status=request_status,
                invitation_status=invitation_status
            )
            for user, role, employee_id, invitation_status, request_status in members
        ]

        result2_for_pagination = await self.session.execute(
            select(UserModel, EmployeeModel.role, EmployeeModel.id, EmployeeModel.invitation_status,
                   EmployeeModel.request_status).join(EmployeeModel,
                                                      EmployeeModel.company_id == company_id).where(
                UserModel.id == EmployeeModel.user_id, EmployeeModel.__table__.c.role != 'Candidate'))
        total_item = len(result2_for_pagination.all())
        total_page = math.ceil(math.ceil(total_item / limit))
        return MembersListResponseWithPagination(data=user_list, total_item=total_item, total_page=total_page)

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
        await self.check_is_user_member(company_id=company_id, user_id=self.user.id)

        stmt = select(EmployeeModel).where(EmployeeModel.company_id == company_id,
                                           EmployeeModel.user_id == self.user.id)
        employees_invitation = await self.session.execute(stmt)

        for employee_invitation in employees_invitation.scalars().all():
            await self.session.delete(employee_invitation)

        await self.session.commit()

    async def member_to_admin(self, user_id: int, company_id: int):

        await self.check_company_owner(company_id=company_id)
        await self.check_is_user_member(company_id=company_id, user_id=user_id)
        existing_employee = await self.session.execute(
            select(EmployeeModel).where(EmployeeModel.company_id == company_id,
                                        EmployeeModel.user_id == user_id))

        worker = existing_employee.scalar()

        worker.role = 'Admin'
        worker.created_at = datetime.utcnow()
        await self.session.commit()

    async def admin_to_member(self, user_id: int, company_id: int):

        await self.check_company_owner(company_id=company_id)
        await self.check_is_user_member(company_id=company_id, user_id=user_id)
        existing_employee = await self.session.execute(
            select(EmployeeModel).where(EmployeeModel.company_id == company_id,
                                        EmployeeModel.user_id == user_id))

        worker = existing_employee.scalar()

        worker.role = 'Member'
        worker.created_at = datetime.utcnow()
        await self.session.commit()

    async def get_company_admins(self, company_id: int, skip: int, limit: int) -> MembersListResponseWithPagination:
        await self.check_company_owner(company_id=company_id)

        user_query = select(UserModel, EmployeeModel.role, EmployeeModel.id, EmployeeModel.invitation_status,
                            EmployeeModel.request_status).join(EmployeeModel,
                                                               EmployeeModel.company_id == company_id).where(
            UserModel.id == EmployeeModel.user_id, EmployeeModel.__table__.c.role == 'Admin').offset(skip).limit(
            limit).order_by('id')
        admins = (await self.session.execute(user_query)).all()
        admin_list = [
            MemberResponse(
                id=admin.id,
                email=admin.email,
                username=admin.username,
                phone_number=admin.phone_number,
                age=admin.age,
                city=admin.city,
                created_at=admin.created_at,
                updated_at=admin.updated_at,
                role=role,
                employee_id=employee_id,
                request_status=request_status,
                invitation_status=invitation_status
            )
            for admin, role, employee_id, invitation_status, request_status in admins
        ]

        result2_for_pagination = await self.session.execute(
            select(UserModel, EmployeeModel.role, EmployeeModel.id, EmployeeModel.invitation_status,
                   EmployeeModel.request_status).join(EmployeeModel, EmployeeModel.company_id == company_id).where(
                UserModel.id == EmployeeModel.user_id, EmployeeModel.__table__.c.role == 'Admin'))

        total_item = len(result2_for_pagination.all())
        total_page = math.ceil(math.ceil(total_item / limit))
        return MembersListResponseWithPagination(data=admin_list, total_item=total_item, total_page=total_page)

    async def checking_for_presence_connections_between_user_company(self, company_id: int, user_id: int) -> None:
        existing_employee = await self.session.execute(
            select(EmployeeModel).where(EmployeeModel.company_id == company_id,
                                        EmployeeModel.user_id == user_id))

        all_existing = existing_employee.fetchall()

        if all_existing:
            raise HTTPException(status_code=status.HTTP_208_ALREADY_REPORTED,
                                detail="An invitation or request already exists for this user")

    async def get_all_candidates(self, company_id: int, limit: int, skip: int) -> UsersListResponseWithPagination:
        await self.check_company_owner(company_id=company_id)

        users_without_companies_query = select(UserModel).filter(~UserModel.company_employees.any())

        users_with_other_companies_query = select(UserModel).filter(
            ~UserModel.company_employees.any(EmployeeModel.company_id == company_id)
        )

        query = users_without_companies_query.union(users_with_other_companies_query).offset(skip).limit(
            limit).order_by('id')

        result = await self.session.execute(query)
        user_list = [UserResponse.model_validate(user, from_attributes=True) for user in
                     result]

        result2_for_pagination = await self.session.execute(
            users_without_companies_query.union(users_with_other_companies_query))
        total_item = len(result2_for_pagination.all())
        total_page = math.ceil(math.ceil(total_item / limit))

        return UsersListResponseWithPagination(data=user_list, total_item=total_item, total_page=total_page)

    async def find_companies(self, skip: int, limit: int) -> CompanyListResponseWithPagination:
        logger.info("Find Companies for user {}".format(self.user.id))

        user_companies_subquery = select(EmployeeModel.company_id).where(
            EmployeeModel.user_id == self.user.id
        )

        companies_query = select(CompanyModel).where(
            ~CompanyModel.id.in_(user_companies_subquery)
        ).offset(skip).limit(limit).order_by('id')

        companies_result = await self.session.execute(companies_query)
        companies_list = [
            CompanyResponse.model_validate(company, from_attributes=True)
            for company in companies_result.scalars()
        ]

        result2_for_pagination = await self.session.execute(
            select(CompanyModel).where(~CompanyModel.id.in_(user_companies_subquery)))
        total_item = len(result2_for_pagination.all())
        total_page = math.ceil(math.ceil(total_item / limit))

        return CompanyListResponseWithPagination(
            data=companies_list,
            total_item=total_item,
            total_page=total_page,
        )

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

    async def check_is_user_member(self, company_id: int, user_id: int):
        query = await self.session.execute(
            select(EmployeeModel).where(EmployeeModel.__table__.c.user_id == user_id,
                                        EmployeeModel.__table__.c.company_id == company_id))
        employee = query.scalars().first()

        if not employee or employee.role == 'Candidate':
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Not Found.")

    @staticmethod
    async def check_candidate_for_request(candidate: EmployeeModel):
        if not candidate.request_status:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="This user is not in the list of candidates.")
