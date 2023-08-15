from fastapi import APIRouter, Depends, status
from starlette.responses import Response

from services.auth import authenticate_and_get_user

from services.invation_service import InvitationService

router = APIRouter()


@router.get("/invitation_send_from_company/{company_id}/user/{user_id}")
async def send_invitation_from_company(invitation_status: str, company_id: int, user_id: int,
                                       current_user=Depends(authenticate_and_get_user),
                                       service: InvitationService = Depends()):
    invitation = await service.send_invitation(company_id=company_id, user_id=user_id,
                                               invitation_status=invitation_status)
    return invitation


@router.get("/{action_id}}/cancel_invitation")
async def cancel_invitation(employee_id: int, current_user=Depends(authenticate_and_get_user),
                            service: InvitationService = Depends()):
    await service.cancel_invitation(employee_id=employee_id)
    return Response(status_code=status.HTTP_200_OK)


@router.get("/{action_id}}/accept_invite")
async def accept_invitation(invitation_status: str, employee_id: int, current_user=Depends(authenticate_and_get_user),
                            service: InvitationService = Depends()):
    await service.accept_invitation(employee_id=employee_id, invitation_status=invitation_status)
    return Response(status_code=status.HTTP_200_OK)


# **************************************************
@router.get("/action/create_from_user/company/{company_id}/")
async def send_request_from_user(invitation_status: str, company_id: int,
                                 current_user=Depends(authenticate_and_get_user),
                                 service: InvitationService = Depends()):
    invitation = await service.send_request(company_id=company_id, invitation_status=invitation_status,
                                            user_id=current_user)
    return invitation


@router.get("/{action_id}}/cancel_invitation")
async def cancel_request(employee_id: int, current_user=Depends(authenticate_and_get_user),
                         service: InvitationService = Depends()):
    await service.cancel_request(employee_id=employee_id)
    return Response(status_code=status.HTTP_200_OK)


@router.get("/{action_id}}/accept_invite")
async def accept_request(invitation_status: str, employee_id: int, current_user=Depends(authenticate_and_get_user),
                         service: InvitationService = Depends()):
    await service.accept_request(employee_id=employee_id, invitation_status=invitation_status)
    return Response(status_code=status.HTTP_200_OK)


# =================================================================
@router.get("/users/{user_id}}/invitation_list")
async def get_users_invitations(invitation_status: str, current_user=Depends(authenticate_and_get_user),
                                service: InvitationService = Depends()):
    invitations = await service.get_user_invitations(current_user_id=current_user.id,
                                                     invitation_status=invitation_status)
    return invitations


@router.get("/users/{user_id}}/requests_list")
async def get_users_requests(requests_status: str, current_user=Depends(authenticate_and_get_user),
                             service: InvitationService = Depends()):
    requests = await service.get_user_requests(current_user_id=current_user.id,
                                               requests_status=requests_status)
    return requests


# **********************************************************
@router.get("/company/{company_id}}/requests_list")
async def get_users_requests(company_id: int, current_user=Depends(authenticate_and_get_user),
                             service: InvitationService = Depends()):
    requests = await service.get_company_requests(current_user_id=current_user.id,
                                                  company_id=company_id)
    print('T' * 50)
    return requests


@router.get("/company/{company_id}}/invitation_list")
async def get_users_invitation(company_id: int, current_user=Depends(authenticate_and_get_user),
                               service: InvitationService = Depends()):
    requests = await service.get_company_invitations(current_user_id=current_user.id,
                                                     company_id=company_id)
    return requests
