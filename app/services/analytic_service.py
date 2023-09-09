import logging
import math
from typing import List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from db.database import get_session
from schemas.analytic_schema import UserCompanyRatingResponse, UserSystemRatingResponse, UserLastPassingOfTheQuiz, \
    AnalyticQuizListResponseWithPagination, AverageScoreInAllQuizzesInAllCompanies, AnalyticsUserAttempt, \
    EmployeeLastQuizCompletionTime, EmployeeSchemaResponse, AverageScoreForAllMembers
from schemas.quiz_schemas import QuizSchemaResponse
from schemas.user_schema import UserResponse
from services.auth import authenticate_and_get_user
from sqlalchemy import select, and_, func
from models.models import (User as UserModel, Quiz as QuizModel, QuizResult as QuizResultModel,
                           Company as CompanyModel, Employee as EmployeeModel)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnalyticsService:
    def __init__(self, session: AsyncSession = Depends(get_session),
                 user: UserModel = Depends(authenticate_and_get_user)):
        self.session = session
        self.user = user

    async def calculate_average_score_in_company(self, user_id: int, company_id: int) -> UserCompanyRatingResponse:
        query = select(func.avg(QuizResultModel.score)).where(
            and_(
                QuizResultModel.user_id == user_id,
                QuizResultModel.company_id == company_id
            )
        )
        result = await self.session.execute(query)
        result_score = result.scalar()
        average_score = round(result_score, 2) if result_score else 0
        return UserCompanyRatingResponse(company_id=company_id, user_id=user_id, average_score=average_score)

    async def calculate_user_rating(self, user_id: int) -> UserSystemRatingResponse:
        query = select(func.avg(QuizResultModel.score)).where(QuizResultModel.user_id == user_id).group_by(
            QuizResultModel.user_id)
        result = await self.session.execute(query)
        result_score = result.scalar()
        average_score = round(result_score, 2) if result_score else 0
        return UserSystemRatingResponse(user_id=user_id, average_score=average_score)

    async def get_all_available_quizzes_list(self, skip: int, limit: int) -> AnalyticQuizListResponseWithPagination:
        quiz_list = (
            select(
                QuizModel,
                func.coalesce(func.max(QuizResultModel.timestamp), func.current_timestamp()).label(
                    "last_completed_time")
            )
            .join(CompanyModel, QuizModel.company_id == CompanyModel.id)
            .join(EmployeeModel, CompanyModel.id == EmployeeModel.company_id)
            .outerjoin(QuizResultModel,
                       and_(QuizModel.id == QuizResultModel.quiz_id, QuizResultModel.user_id == self.user.id))
            .filter(EmployeeModel.user_id == self.user.id, EmployeeModel.role != "Candidate",
                    QuizModel.is_deleted == False, )
            .group_by(QuizModel.id)
        )

        quizzes = await self.session.execute(quiz_list.offset(skip).limit(limit))
        quizzes_all = quizzes.all()

        quizzes_list_result = [UserLastPassingOfTheQuiz(
            quiz=QuizSchemaResponse(
                id=quiz.id,
                title=quiz.title,
                company_id=quiz.company_id,
                user_id=quiz.user_id,
                description=quiz.description,
                frequency_in_days=quiz.frequency_in_days),

            date=last_completed_time)
            for quiz, last_completed_time in quizzes_all
        ]

        items = await self.session.execute(quiz_list)
        total_item = len(items.all())
        total_page = math.ceil(math.ceil(total_item / limit))
        return AnalyticQuizListResponseWithPagination(data=quizzes_list_result, total_item=total_item,
                                                      total_page=total_page)

    async def list_of_average_in_all_quizzes_in_all_companies(self, user_id: int) \
            -> List[AverageScoreInAllQuizzesInAllCompanies]:
        stmt = select(QuizResultModel).join(QuizModel, QuizResultModel.quiz_id == QuizModel.id).where(
            QuizResultModel.user_id == user_id)

        user_quiz_result = await self.session.execute(stmt)
        quizzes_list = user_quiz_result.scalars()

        average_scores_dict = {}

        for quiz_res in quizzes_list:
            if quiz_res.quiz_id not in average_scores_dict:

                average_scores_dict[quiz_res.quiz_id] = {
                    'quiz_id': quiz_res.quiz_id,
                    'company_id': quiz_res.company_id,
                    'score': [{
                        'quiz_result_id': quiz_res.id,
                        'timestamp': quiz_res.timestamp,
                        'total_question': quiz_res.total_question,
                        'total_correct_answers': quiz_res.total_answers,
                        'average_score': round(quiz_res.total_answers / quiz_res.total_question * 100, 2),

                    }]
                }
            else:
                total_question = average_scores_dict[quiz_res.quiz_id]['score'][-1][
                                     'total_question'] + quiz_res.total_question
                total_correct_answers = average_scores_dict[quiz_res.quiz_id]['score'][-1][
                                            'total_correct_answers'] + quiz_res.total_answers

                average_scores_dict[quiz_res.quiz_id]['score'].append(
                    {
                        'quiz_result_id': quiz_res.id,
                        'total_question': total_question,
                        'total_correct_answers': total_correct_answers,
                        'average_score': round(total_correct_answers / total_question * 100, 2),
                        'timestamp': quiz_res.timestamp
                    }
                )
        attempts = [
            AverageScoreInAllQuizzesInAllCompanies(
                quiz_id=key,
                company_id=value['company_id'],
                score=[
                    AnalyticsUserAttempt(
                        quiz_result_id=score_item['quiz_result_id'],
                        total_question=score_item['total_question'],
                        total_correct_answers=score_item['total_correct_answers'],
                        average_score=score_item['average_score'],
                        timestamp=score_item['timestamp']
                    )
                    for score_item in value['score']
                ]
            )
            for key, value in average_scores_dict.items()
        ]
        return attempts

    async def members_last_attempt(self, company_id: int, skip: int, limit: int) \
            -> List[EmployeeLastQuizCompletionTime]:
        query = (
            select(
                EmployeeModel,
                func.max(QuizResultModel.timestamp).label("last_completed_time")
            )
            .join(CompanyModel, EmployeeModel.company_id == CompanyModel.id).where(CompanyModel.id == company_id)
            .join(QuizModel, CompanyModel.id == QuizModel.company_id)
            .outerjoin(QuizResultModel,
                       and_(QuizModel.id == QuizResultModel.quiz_id, QuizResultModel.user_id == EmployeeModel.user_id))
            .filter(EmployeeModel.role != "Candidate")
            .group_by(EmployeeModel.id)
        )

        result = await self.session.execute(query.offset(skip).limit(limit))
        rows = result.all()

        employee_last_quiz_completion_times = []

        for row in rows:
            employee, last_completed_time = row
            member_query = await self.session.get(UserModel, employee.user_id)
            member = UserResponse.model_validate(member_query, from_attributes=True)
            last_completed_time_dt = datetime.utcfromtimestamp(
                last_completed_time.timestamp()) if last_completed_time else None
            employee_last_quiz_completion_times.append(EmployeeLastQuizCompletionTime(
                employee=EmployeeSchemaResponse(
                    id=employee.id,
                    member=member,
                    company_id=employee.company_id,
                    role=employee.role
                ),
                last_completed_time=last_completed_time_dt
            ))
        return employee_last_quiz_completion_times

    async def list_of_average_all_members_for_current_quiz(self, company_id: int, quiz_id: int) \
            -> List[AverageScoreForAllMembers]:
        stmt = select(QuizResultModel).filter(QuizResultModel.company_id == company_id,
                                              QuizResultModel.quiz_id == quiz_id).order_by(
            QuizResultModel.timestamp)

        stmt_result = await self.session.execute(stmt)
        quizzes_list = stmt_result.scalars()

        average_scores_dict = {}

        for quiz_res in quizzes_list:
            if quiz_res.user_id not in average_scores_dict:
                member_query = await self.session.get(UserModel, quiz_res.user_id)
                member = UserResponse.model_validate(member_query, from_attributes=True)

                average_scores_dict[quiz_res.user_id] = {
                    'quiz_id': quiz_res.quiz_id,
                    'member': member,
                    'company_id': quiz_res.company_id,
                    'score': [{
                        'quiz_result_id': quiz_res.id,
                        'total_question': quiz_res.total_question,
                        'total_correct_answers': quiz_res.total_answers,
                        'average_score': round(quiz_res.total_answers / quiz_res.total_question * 100, 2),
                        'timestamp': quiz_res.timestamp,

                    }]
                }
            else:
                total_question = average_scores_dict[quiz_res.user_id]['score'][-1][
                                     'total_question'] + quiz_res.total_question
                total_correct_answers = average_scores_dict[quiz_res.user_id]['score'][-1][
                                            'total_correct_answers'] + quiz_res.total_answers

                average_scores_dict[quiz_res.user_id]['score'].append(
                    {
                        'quiz_result_id': quiz_res.id,
                        'total_question': total_question,
                        'total_correct_answers': total_correct_answers,
                        'average_score': round(total_correct_answers / total_question * 100, 2),
                        'timestamp': quiz_res.timestamp
                    }
                )
        members = [
            AverageScoreForAllMembers(
                quiz_id=key,
                member=value['member'],
                company_id=value['company_id'],
                score=[
                    AnalyticsUserAttempt(
                        quiz_result_id=score_item['quiz_result_id'],
                        total_question=score_item['total_question'],
                        total_correct_answers=score_item['total_correct_answers'],
                        average_score=score_item['average_score'],
                        timestamp=score_item['timestamp']
                    )
                    for score_item in value['score']
                ]
            )
            for key, value in average_scores_dict.items()
        ]

        return members
