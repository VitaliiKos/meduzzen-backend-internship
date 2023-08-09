from fastapi import APIRouter, Depends, status
from starlette.responses import Response

from db.database import get_session
from schemas.company_schema import CompanyListResponse, CompanyResponse, CompanyCreate, CompanyUpdateInfo
from services.auth import authenticate_and_get_user

from services.company_service import CompanyService

router = APIRouter()


@router.get("/company", response_model=CompanyListResponse)
async def get_companies(skip: int = 0, limit: int = 10, session=Depends(get_session)) -> CompanyListResponse:
    company_service = CompanyService(session=session)
    companies = await company_service.get_all_companies(skip=skip, limit=limit)
    return companies


@router.get("/company/{company_id}", response_model=CompanyResponse)
async def get_company(company_id: int, session=Depends(get_session)) -> CompanyResponse:
    company_service = CompanyService(session=session)
    company = await company_service.get_company_by_id(company_id=company_id)
    return company


@router.post("/company", response_model=CompanyResponse)
async def create_company(company_data: CompanyCreate, current_user=Depends(authenticate_and_get_user),
                         service: CompanyService = Depends()) -> CompanyCreate:
    company = await service.create_company(company_data=company_data, current_user_id=current_user.id)
    return company


@router.put("/company/{company_id}/info", response_model=CompanyResponse)
async def update_company(company_id: int, company_data: CompanyUpdateInfo,
                         current_user=Depends(authenticate_and_get_user),
                         service: CompanyService = Depends()) -> CompanyResponse:
    company = await service.update_company(company_id=company_id, company_data=company_data,
                                           current_user_id=current_user.id)
    return company


@router.put("/company/{company_id}/status", response_model=CompanyResponse)
async def update_company_status(company_id: int, current_user=Depends(authenticate_and_get_user),
                                service: CompanyService = Depends()) -> CompanyResponse:
    company = await service.update_company_status(company_id=company_id, current_user_id=current_user.id)
    return company


@router.delete("/company/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(company_id: int, current_user=Depends(authenticate_and_get_user),
                         service: CompanyService = Depends()) -> Response:
    await service.delete_company(company_id=company_id, current_user_id=current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
