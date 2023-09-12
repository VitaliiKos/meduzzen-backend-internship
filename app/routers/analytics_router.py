from typing import List

from fastapi import APIRouter, Depends

from schemas.analytic_schema import UserCompanyRatingResponse, UserSystemRatingResponse, \
    AnalyticQuizListResponseWithPagination, AverageScoreInAllQuizzesInAllCompanies, EmployeeLastQuizCompletionTime, \
    AverageScoreForAllMembers
from services.analytic_service import AnalyticsService

router = APIRouter()


@router.get("/user/{user_id}/user_average/company/{company_id}", response_model=UserCompanyRatingResponse)
async def user_average_in_company(company_id: int, user_id: int,
                                  service: AnalyticsService = Depends()) -> UserCompanyRatingResponse:
    average = await service.calculate_average_score_in_company(company_id=company_id, user_id=user_id)
    return average


@router.get("/user/{user_id}/user_system_rating", response_model=UserSystemRatingResponse)
async def user_rating_in_system(user_id: int, service: AnalyticsService = Depends()) -> UserSystemRatingResponse:
    average = await service.calculate_user_rating(user_id=user_id)
    return average


@router.get("/user/quizzes", response_model=AnalyticQuizListResponseWithPagination)
async def list_of_all_available_quizzes(skip: int = 0, limit: int = 5, service: AnalyticsService = Depends()) \
        -> AnalyticQuizListResponseWithPagination:
    list_of_quizzes = await service.get_all_available_quizzes_list(skip=skip, limit=limit)
    return list_of_quizzes


@router.get("/user/{user_id}/companies/quizzes", response_model=list[AverageScoreInAllQuizzesInAllCompanies])
async def list_of_average_in_all_quizzes_in_all_companies(user_id: int, service: AnalyticsService = Depends()) \
        -> list[AverageScoreInAllQuizzesInAllCompanies]:
    list_of_average = await service.list_of_average_in_all_quizzes_in_all_companies(user_id=user_id)
    return list_of_average


@router.get("/company/{company_id}/members/last_attempt", response_model=List[EmployeeLastQuizCompletionTime])
async def members_last_attempt(company_id: int, skip: int = 0, limit: int = 5, service: AnalyticsService = Depends()) \
        -> list[EmployeeLastQuizCompletionTime]:
    member_list = await service.members_last_attempt(company_id=company_id, skip=skip, limit=limit)
    return member_list


@router.get("/company/{company_id}/users/quizzes/{quiz_id}", response_model=list[AverageScoreForAllMembers])
async def list_of_average_all_members_for_current_quiz(company_id: int, quiz_id: int,
                                                       service: AnalyticsService = Depends()) \
        -> list[AverageScoreForAllMembers]:
    list_of_average_score = await service.list_of_average_all_members_for_current_quiz(company_id=company_id,
                                                                                       quiz_id=quiz_id)
    return list_of_average_score
