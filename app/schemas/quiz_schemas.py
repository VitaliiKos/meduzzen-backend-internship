from typing import List, Optional

from pydantic import BaseModel


class AnswerSchemaCreate(BaseModel):
    answer_text: str
    is_correct: bool


class AnswerSchemaResponse(BaseModel):
    id: int
    answer_text: str
    is_correct: bool
    question_id: int


class QuestionSchemaCreate(BaseModel):
    question_text: str
    answers: List[AnswerSchemaCreate]


class QuestionSchemaResponse(BaseModel):
    id: int
    quiz_id: int
    question_text: str
    answers: List[AnswerSchemaResponse]


# Pydantic schema for Quiz model
class QuizSchema(BaseModel):
    id: int
    title: str
    company_id: int
    user_id: int
    description: Optional[str]
    frequency_in_days: int
    questions: List[QuestionSchemaResponse]


class CreateQuizRequest(BaseModel):
    title: str
    description: str
    frequency_in_days: int
    questions_data: List[QuestionSchemaCreate]
    company_id: int


class QuizSchemaResponse(BaseModel):
    title: str
    description: str
    frequency_in_days: int
    company_id: int
    user_id: int
    id: int


class QuizzesListResponseWithPagination(BaseModel):
    total_item: int
    total_page: int
    data: List[QuizSchemaResponse]

    class Config:
        from_attributes = True


class UpdateQuizRequest(BaseModel):
    title: str
    description: str
    frequency_in_days: int


class UpdateQuestionRequest(BaseModel):
    question_text: str


# class CreateQuestionRequest(UpdateQuestionRequest):
#     answers_data: [AnswerSchemaCreate]


class UpdateQuestionResponse(BaseModel):
    id: int
    quiz_id: int
    question_text: str


class CreateQuestionResponse(UpdateQuestionResponse):
    pass
