from fastapi import APIRouter, Depends, status
from starlette.responses import Response
from schemas.quiz_schemas import CreateQuizRequest, QuizSchemaResponse, QuizSchema, UpdateQuizRequest, \
    UpdateQuestionRequest, UpdateQuestionResponse, AnswerSchemaCreate, AnswerSchemaResponse
from services.quizzes__service import QuizzesService

router = APIRouter()


@router.post("/quiz", response_model=QuizSchemaResponse)
async def create_quiz(request_data: CreateQuizRequest,
                      service: QuizzesService = Depends()) -> QuizSchemaResponse:
    quiz = await service.create_quiz(title=request_data.title, description=request_data.description,
                                     frequency_in_days=request_data.frequency_in_days,
                                     company_id=request_data.company_id, questions_data=request_data.questions_data)
    return QuizSchemaResponse.model_validate(quiz, from_attributes=True)


@router.get("/quiz/{quiz_id}", response_model=QuizSchema)
async def get_quiz_by_id(quiz_id: int, service: QuizzesService = Depends()) -> QuizSchema:
    quiz = await service.get_quiz_by_id(quiz_id=quiz_id)
    return quiz


@router.get("/quiz/company/{company_id}")
async def get_quiz_by_company(company_id: int, skip: int = 0, limit: int = 5, service: QuizzesService = Depends()):
    quiz = await service.get_quiz_by_company_id(company_id=company_id, skip=skip, limit=limit)
    return quiz


@router.delete("/quiz/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quiz_by_id(quiz_id: int, service: QuizzesService = Depends()) -> Response:
    await service.delete_quiz_by_id(quiz_id=quiz_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/quiz/{quiz_id}", response_model=QuizSchemaResponse)
async def update_quiz(quiz_id: int, request_data: UpdateQuizRequest,
                      service: QuizzesService = Depends()) -> QuizSchemaResponse:
    quiz = await service.update_quiz(quiz_id=quiz_id,
                                     title=request_data.title,
                                     description=request_data.description,
                                     frequency_in_days=request_data.frequency_in_days)
    return QuizSchemaResponse.model_validate(quiz, from_attributes=True)


@router.put("/quiz/question/{question_id}", response_model=UpdateQuestionResponse)
async def update_quiz_question(question_id: int, request_data: UpdateQuestionRequest,
                               service: QuizzesService = Depends()) -> UpdateQuestionResponse:
    question = await service.update_quiz_question(question_id=question_id,
                                                  question_text=request_data.question_text)
    return question


@router.put("/quiz/question/{question_id}/answer/{answer_id}", response_model=AnswerSchemaResponse)
async def update_question_answer(question_id: int, answer_id: int, request_data: AnswerSchemaCreate,
                                 service: QuizzesService = Depends()) -> AnswerSchemaResponse:
    answer = await service.update_question_answer(answer_id=answer_id,
                                                  question_id=question_id,
                                                  answer_text=request_data.answer_text,
                                                  is_correct=request_data.is_correct)
    return AnswerSchemaResponse.model_validate(answer, from_attributes=True)
