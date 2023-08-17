from fastapi import APIRouter, Depends, status
from starlette.responses import Response

from db.database import get_session
from models.models import Company
from schemas.company_schema import CompanyListResponseWithPagination, CompanyResponse, \
    CompanyCreate, CompanyUpdateInfo, UserCompanyRole
from services.auth import authenticate_and_get_user

from services.company_service import CompanyService

router = APIRouter()


@router.get("/company", response_model=CompanyListResponseWithPagination)
async def get_companies(skip: int = 0, limit: int = 5,
                        session=Depends(get_session)) -> CompanyListResponseWithPagination:
    company_service = CompanyService(session=session)
    companies = await company_service.get_all_companies(skip=skip, limit=limit)
    return companies


@router.get("/company/{company_id}", response_model=CompanyResponse)
async def get_company(company_id: int, service: CompanyService = Depends()) -> CompanyResponse:
    company = await service.get_company_by_id(company_id=company_id)
    return company


@router.post("/company", response_model=CompanyResponse)
async def create_company(company_data: CompanyCreate, current_user=Depends(authenticate_and_get_user),
                         service: CompanyService = Depends()) -> Company:
    company = await service.create_company(company_data=company_data, current_user_id=current_user.id)
    return company


@router.put("/company/{company_id}/info", response_model=CompanyResponse)
async def update_company(company_id: int, company_data: CompanyUpdateInfo,
                         service: CompanyService = Depends()) -> CompanyResponse:
    company = await service.update_company(company_id=company_id, company_data=company_data)
    return company


@router.put("/company/{company_id}/status", response_model=CompanyResponse)
async def update_company_status(company_id: int, service: CompanyService = Depends()) -> CompanyResponse:
    company = await service.update_company_status(company_id=company_id)
    return company


@router.delete("/company/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(company_id: int, service: CompanyService = Depends()) -> Response:
    await service.delete_company(company_id=company_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/my_company/", response_model=CompanyListResponseWithPagination)
async def get_my_companies(skip: int = 0, limit: int = 5, current_user=Depends(authenticate_and_get_user),
                           service: CompanyService = Depends()) -> CompanyListResponseWithPagination:
    companies = await service.get_my_companies(skip=skip, limit=limit, current_user_id=current_user.id)
    return companies


@router.get("/company/{company_id}/user_role", response_model=UserCompanyRole)
async def get_user_role(company_id: int, current_user=Depends(authenticate_and_get_user),
                        service: CompanyService = Depends()) -> UserCompanyRole:
    user_role = await service.get_company_by_id_with_role(company_id=company_id, current_user_id=current_user.id)
    return user_role
