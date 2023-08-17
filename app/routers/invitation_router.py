from fastapi import APIRouter, Depends, status
from starlette.responses import Response

from models.models import Employee
from schemas.employee import EmployeeRequestResponse, EmployeeInvitationResponse, EmployeeListInvitations, \
    EmployeeListRequest
from schemas.user_schema import UsersListResponse
from services.auth import authenticate_and_get_user

from services.invation_service import InvitationService

router = APIRouter()


@router.get("/invitation_send_from_company/{company_id}/user/{user_id}", response_model=EmployeeInvitationResponse)
async def send_invitation_from_company(company_id: int, user_id: int, invitation_status: str = 'padding',
                                       service: InvitationService = Depends()) -> Employee:
    invitation = await service.send_invitation_from_company(company_id=company_id, user_id=user_id,
                                                            invitation_status=invitation_status)
    return invitation


@router.get("/{action_id}/cancel_invitation", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_invitation(employee_id: int, service: InvitationService = Depends()) -> Response:
    await service.cancel_invitation_request(employee_id=employee_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{action_id}/accept_invite", status_code=status.HTTP_200_OK)
async def accept_invitation(employee_id: int, invitation_status: str = 'accept',
                            service: InvitationService = Depends()) -> Response:
    await service.accept_invitation(employee_id=employee_id, invitation_status=invitation_status)
    return Response(status_code=status.HTTP_200_OK)


@router.get("/action/create_from_user/company/{company_id}/", response_model=EmployeeRequestResponse)
async def send_request_from_user(invitation_status: str, company_id: int,
                                 service: InvitationService = Depends()) -> Employee:
    invitation = await service.send_request(company_id=company_id, invitation_status=invitation_status,
                                            )
    return invitation


@router.get("/{action_id}/cancel_request", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_request(employee_id: int, service: InvitationService = Depends()) -> Response:
    await service.cancel_invitation_request(employee_id=employee_id)
    return Response(status_code=status.HTTP_200_OK)


@router.get("/{action_id}/accept_request", status_code=status.HTTP_200_OK)
async def accept_request(employee_id: int, invitation_status: str = 'accept',
                         service: InvitationService = Depends()) -> Response:
    await service.accept_request(employee_id=employee_id, invitation_status=invitation_status)
    return Response(status_code=status.HTTP_200_OK)


@router.get("/users/{user_id}/invitation_list", response_model=EmployeeListInvitations)
async def get_users_invitations(invitation_status: str = 'accept', skip: int = 0, limit: int = 5,
                                service: InvitationService = Depends()) -> EmployeeListInvitations:
    invitations = await service.get_user_invitations(invitation_status=invitation_status, skip=skip, limit=limit)
    return invitations


@router.get("/users/{user_id}/requests_list", response_model=EmployeeListRequest)
async def get_users_requests(request_status: str = 'padding', skip: int = 0, limit: int = 5,
                             service: InvitationService = Depends()) -> EmployeeListRequest:
    requests = await service.get_user_requests(request_status=request_status, skip=skip, limit=limit)
    return requests


@router.get("/company/{company_id}/requests_list", response_model=EmployeeListRequest)
async def get_company_requests_list(company_id: int, request_status: str = 'padding', skip: int = 0, limit: int = 5,
                                    service: InvitationService = Depends()) -> EmployeeListRequest:
    requests_employee = await service.get_company_requests(company_id=company_id, request_status=request_status,
                                                           skip=skip, limit=limit)

    return requests_employee


@router.get("/company/{company_id}/invitation_list", response_model=EmployeeListInvitations)
async def get_company_invitations_list(company_id: int, invitation_status: str = 'padding', skip: int = 0,
                                       limit: int = 5,
                                       service: InvitationService = Depends()) -> EmployeeListInvitations:
    requests = await service.get_company_invitations(company_id=company_id, invitation_status=invitation_status,
                                                     skip=skip, limit=limit)
    return requests


@router.get("/company/{company_id}/members", response_model=UsersListResponse)
async def get_company_members_list(company_id: int, skip: int = 0, limit: int = 5,
                                   service: InvitationService = Depends()) -> UsersListResponse:
    requests = await service.get_company_members(company_id=company_id, skip=skip, limit=limit)
    return requests


@router.get("/{action_id}/dismiss_employee/", status_code=status.HTTP_204_NO_CONTENT)
async def remove_worker_from_company_by_owner(company_id: int, user_id: int,
                                              service: InvitationService = Depends()) -> Response:
    await service.remove_worker_from_company(company_id=company_id, user_id=user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{action_id}/leave_company/", status_code=status.HTTP_204_NO_CONTENT)
async def resign_from_the_company(company_id: int, service: InvitationService = Depends()) -> Response:
    await service.leave_company(company_id=company_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
