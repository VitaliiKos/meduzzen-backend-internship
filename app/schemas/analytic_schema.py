from typing import List, Optional

from pydantic import BaseModel
from datetime import datetime

from schemas.quiz_schemas import QuizSchemaResponse
from schemas.user_schema import UserResponse


class UserCompanyRatingResponse(BaseModel):
    company_id: int
    user_id: int
    average_score: float


class UserSystemRatingResponse(BaseModel):
    user_id: int
    average_score: float


class UserLastPassingOfTheQuiz(BaseModel):
    quiz: QuizSchemaResponse
    date: datetime


class AnalyticQuizListResponseWithPagination(BaseModel):
    total_item: int
    total_page: int
    data: List[UserLastPassingOfTheQuiz]

    class Config:
        from_attributes = True


class AnalyticsUserAttempt(BaseModel):
    quiz_result_id: int
    total_question: int
    total_correct_answers: int
    average_score: float
    timestamp: datetime


class AverageScoreInAllQuizzesInAllCompanies(BaseModel):
    quiz_id: int
    score: List[AnalyticsUserAttempt]


class AverageScoreForAllMembers(BaseModel):
    user_id: int
    member: UserResponse
    score: List[AnalyticsUserAttempt]


class EmployeeSchemaResponse(BaseModel):
    id: int
    member: UserResponse
    company_id: int
    role: str


class EmployeeLastQuizCompletionTime(BaseModel):
    employee: EmployeeSchemaResponse
    last_completed_time: Optional[datetime]
