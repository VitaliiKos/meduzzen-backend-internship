import json
import math
import logging
from uuid import uuid4
from typing import List
from datetime import datetime
import redis.asyncio as redis
from sqlalchemy import select, update, and_, func
from sqlalchemy.orm import joinedload
from fastapi import HTTPException, status

from models.models import Quiz as QuizModel, Question as QuestionModel, Answer as AnswerModel, \
    QuizResult as QuizResultModel, QuizResult
from schemas.quiz_schemas import QuestionSchemaCreate, QuestionSchemaResponse, QuizSchema, AnswerSchemaResponse, \
    QuizSchemaResponse, QuizzesListResponseWithPagination, AnswerSchemaCreate, UserCompanyRatingResponse, \
    UserSystemRatingResponse, UserQuizVote
from services.invation_service import InvitationService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QuizzesService(InvitationService):
    async def get_quiz_by_id(self, quiz_id: int) -> QuizSchema:
        try:
            stmt = select(QuizModel).filter(QuizModel.id == quiz_id).options(
                joinedload(QuizModel.questions).joinedload(QuestionModel.answers))
            result_stmt = await self.session.execute(stmt)
            my_quiz = result_stmt.scalar()
            questions_data = []
            for question in my_quiz.questions:
                answers_data = [AnswerSchemaResponse.model_validate(answer, from_attributes=True) for answer in
                                question.answers]

                question_data = QuestionSchemaResponse(
                    id=question.id,
                    quiz_id=question.quiz_id,
                    question_text=question.question_text,
                    answers=answers_data
                )
                questions_data.append(question_data)

            quiz_data = QuizSchema(
                id=my_quiz.id,
                company_id=my_quiz.company_id,
                user_id=my_quiz.user_id,
                title=my_quiz.title,
                description=my_quiz.description,
                frequency_in_days=my_quiz.frequency_in_days,
                questions=questions_data
            )

            return quiz_data
        except Exception as error:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not found')

    async def create_quiz(self, company_id: int, title: str, description: str, frequency_in_days: int,
                          questions_data: list[QuestionSchemaCreate]) -> QuizModel:
        await self.check_company_owner(company_id=company_id)
        employee = await self.check_company_role(user_id=self.user.id, company_id=company_id)

        if employee.role.strip().lower() not in ['admin', 'owner']:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You don't have permission!")

        if len(questions_data) < 2:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Quiz mast have more than two questions")
        try:
            for question in questions_data:
                answers_data = question.answers

                if len(answers_data) < 2:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                        detail="Each question must have at least two answer options.")

            quiz = QuizModel(title=title, description=description, frequency_in_days=frequency_in_days,
                             company_id=company_id, user_id=self.user.id)
            self.session.add(quiz)
            await self.session.commit()

            for question in questions_data:
                question_text = question.question_text
                answers_data = question.answers

                question = QuestionModel(quiz_id=quiz.id, question_text=question_text)
                self.session.add(question)
                await self.session.commit()

                for answer_data in answers_data:
                    answer_text = answer_data.answer_text
                    is_correct = answer_data.is_correct

                    answer = AnswerModel(question_id=question.id, answer_text=answer_text, is_correct=is_correct)
                    self.session.add(answer)
                    await self.session.commit()
            return quiz

        except Exception as error:
            await self.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    async def get_quiz_by_company_id(self, company_id: int, skip: int, limit: int) -> QuizzesListResponseWithPagination:
        stmt = select(QuizModel).where(QuizModel.company_id == company_id).offset(skip).limit(limit).order_by(
            -QuizModel.id)
        quizzes = await self.session.execute(stmt)
        if not quizzes:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Not Found')

        quiz_list = [QuizSchemaResponse.model_validate(quiz, from_attributes=True) for quiz in quizzes.scalars()]

        items = await self.session.execute(select(QuizModel).where(QuizModel.company_id == company_id))
        total_item = len(items.all())
        total_page = math.ceil(math.ceil(total_item / limit))

        return QuizzesListResponseWithPagination(data=quiz_list, total_item=total_item, total_page=total_page)

    async def delete_quiz_by_id(self, quiz_id: int) -> None:
        stmt = await self.session.get(QuizModel, quiz_id)

        if not stmt:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='NOT FOUND')

        await self.check_company_owner(company_id=stmt.company_id)
        employee = await self.check_company_role(user_id=self.user.id, company_id=stmt.company_id)

        if employee.role.strip().lower() not in ['admin', 'owner']:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You don't have permission!")

        await self.session.delete(stmt)
        await self.session.commit()

    async def update_quiz(self, quiz_id: int, title: str, description: str, frequency_in_days: int):
        try:
            quiz = await self.get_quiz_by_id(quiz_id=quiz_id)
            if not quiz:
                raise HTTPException(status_code=404, detail="Quiz not found")

            await self.check_user_permission_for_quiz(user_id=self.user.id, company_id=quiz.company_id)

            stmt = (update(QuizModel).where(QuizModel.id == quiz.id).values(
                title=title, description=description, frequency_in_days=frequency_in_days).returning(QuizModel))

            result = await self.session.execute(stmt)
            updated_quiz = result.scalar()

            await self.session.commit()
            return updated_quiz

        except Exception as e:
            await self.session.rollback()
            raise e

    async def update_quiz_question(self, question_id: int, question_text: str):
        try:
            stmt = await self.session.get(QuestionModel, question_id)
            if not stmt:
                raise HTTPException(status_code=404, detail="Quiz question not found")

            quiz = await self.get_quiz_by_id(quiz_id=stmt.quiz_id)

            if not quiz:
                raise HTTPException(status_code=404, detail="Quiz not found")

            await self.check_user_permission_for_quiz(user_id=self.user.id, company_id=quiz.company_id)

            stmt = (update(QuestionModel).where(QuestionModel.id == question_id).values(
                question_text=question_text).returning(QuestionModel))

            result = await self.session.execute(stmt)
            updated_quiz_question = result.scalar()

            await self.session.commit()
            return updated_quiz_question

        except Exception as e:
            await self.session.rollback()
            raise e

    async def update_question_answer(self, question_id: int, answer_id: int, answer_text: str,
                                     is_correct: bool) -> AnswerModel:
        try:
            stmt_quiz = select(QuizModel).join(QuestionModel, QuestionModel.id == question_id).where(
                QuizModel.id == QuestionModel.quiz_id)
            quiz_query = await self.session.execute(stmt_quiz)
            quiz = quiz_query.scalar()

            if not quiz:
                raise HTTPException(status_code=404, detail="Quiz not found")

            await self.check_user_permission_for_quiz(user_id=self.user.id, company_id=quiz.company_id)

            stmt_answer = (update(AnswerModel).where(AnswerModel.id == answer_id).values(
                answer_text=answer_text, is_correct=is_correct).returning(AnswerModel))

            result = await self.session.execute(stmt_answer)
            updated_quiz_question = result.scalar()

            await self.session.commit()
            return updated_quiz_question

        except Exception as e:
            await self.session.rollback()
            raise e

    async def delete_question_answer(self, answer_id: int, quiz_id: int) -> None:
        stmt_quiz = await self.session.get(QuizModel, quiz_id)
        stmt_answer = await self.session.get(AnswerModel, answer_id)

        if not stmt_quiz or not stmt_answer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='NOT FOUND')

        await self.check_company_owner(company_id=stmt_quiz.company_id)
        employee = await self.check_company_role(user_id=self.user.id, company_id=stmt_quiz.company_id)

        if employee.role.strip().lower() not in ['admin', 'owner']:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You don't have permission!")

        await self.session.delete(stmt_answer)
        await self.session.commit()

    async def delete_quiz_question(self, question_id: int, quiz_id: int) -> None:
        stmt_quiz = await self.session.get(QuizModel, quiz_id)
        stmt_question = await self.session.get(QuestionModel, question_id)

        if not stmt_quiz or not stmt_question:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='NOT FOUND')

        await self.check_company_owner(company_id=stmt_quiz.company_id)
        employee = await self.check_company_role(user_id=self.user.id, company_id=stmt_quiz.company_id)

        if employee.role.strip().lower() not in ['admin', 'owner']:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You don't have permission!")

        await self.session.delete(stmt_question)
        await self.session.commit()

    async def create_quiz_question(self, quiz_id: int, question_text: str,
                                   answers: List[AnswerSchemaCreate]) -> QuestionModel:
        stmt_quiz = await self.session.get(QuizModel, quiz_id)

        await self.check_company_owner(company_id=stmt_quiz.company_id)
        employee = await self.check_company_role(user_id=self.user.id, company_id=stmt_quiz.company_id)

        if employee.role.strip().lower() not in ['admin', 'owner']:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You don't have permission!")

        try:
            if len(answers) < 2:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Each question must have at least two answer options.")

            question = QuestionModel(question_text=question_text, quiz_id=quiz_id)
            self.session.add(question)
            await self.session.commit()

            for answer_data in answers:
                answer_text = answer_data.answer_text
                is_correct = answer_data.is_correct

                answer = AnswerModel(question_id=question.id, answer_text=answer_text, is_correct=is_correct)
                self.session.add(answer)
                await self.session.commit()
            return question

        except Exception as error:
            await self.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    async def create_question_answer(self, question_id: int, answer_text: str, is_correct: bool) -> AnswerModel:
        stmt_question = await self.session.get(QuestionModel, question_id)
        if not stmt_question:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='NOT FOUND')

        stmt_quiz = await self.session.get(QuizModel, stmt_question.quiz_id)

        await self.check_company_owner(company_id=stmt_quiz.company_id)
        employee = await self.check_company_role(user_id=self.user.id, company_id=stmt_quiz.company_id)

        if employee.role.strip().lower() not in ['admin', 'owner']:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You don't have permission!")
        try:

            answer_text = answer_text
            is_correct = is_correct

            answer = AnswerModel(question_id=question_id, answer_text=answer_text, is_correct=is_correct)
            self.session.add(answer)
            await self.session.commit()
            return answer

        except Exception as error:
            await self.session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    async def quiz_vote(self, company_id: int, quiz_id: int, vote_data: dict) -> QuizResult:
        connection = await redis.Redis(host='localhost', port=6379, encoding='utf-8', decode_responses=True)

        try:

            quiz = await self.get_quiz_by_id(quiz_id=quiz_id)

            if not quiz:
                raise HTTPException(status_code=404, detail="Quiz not found")
            total_answers = 0
            total_questions = 0

            for question in quiz.questions:
                total_questions += 1
                answer = list(filter(lambda x: x.id == vote_data.get(str(question.id)), question.answers))
                correct_answer = list(filter(lambda x: x.is_correct, question.answers))
                if answer:
                    total_answers += 1 if answer[0].is_correct else 0
                    await self.save_quiz_vote_to_redis(company_id=company_id, quiz_id=quiz_id, user_id=self.user.id,
                                                       question_text=question.question_text,
                                                       answer_text=answer[0].answer_text,
                                                       is_correct=answer[0].is_correct,
                                                       correct_answer=correct_answer[0].answer_text,
                                                       connection=connection)
            score = round(total_answers / total_questions * 100, 2)

            quiz_result = QuizResultModel(
                user_id=self.user.id,
                quiz_id=quiz_id,
                company_id=company_id,
                total_question=total_questions,
                total_answers=total_answers,
                score=score,
                timestamp=datetime.utcnow()
            )

            self.session.add(quiz_result)
            await self.session.commit()

            return quiz_result

        except Exception as e:
            await self.session.rollback()
            raise e
        finally:
            await connection.close()

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

    async def check_user_permission_for_quiz(self, user_id: int, company_id: int) -> None:
        employee = await self.check_company_role(user_id=user_id, company_id=company_id)

        if employee.role.strip().lower() not in ['admin', 'owner']:
            raise HTTPException(status_code=403, detail="You don't have permission to update this quiz")

    @staticmethod
    async def save_quiz_vote_to_redis(user_id: int, company_id: int, quiz_id: int, question_text: str,
                                      answer_text: str, is_correct: bool, correct_answer: str, connection) -> None:
        try:
            answer_key = f"user:{user_id}:company:{company_id}:quiz_id:{quiz_id}:uuid{str(uuid4())}"

            answer_data = {
                "question_text": question_text,
                "answer_text": answer_text,
                "is_correct": is_correct,
                "correct_answer": correct_answer
            }

            await connection.set(answer_key, ex=172800, value=json.dumps(answer_data))
        except Exception as e:
            raise e

    async def get_quiz_votes_from_redis(self, quiz_id: int) -> list[UserQuizVote]:
        try:
            connection = await redis.Redis(host='localhost', port=6379, encoding='utf-8', decode_responses=True)

            user_key_pattern = f"user:{self.user.id}:*:quiz_id:{quiz_id}:*"
            user_keys = await connection.keys(user_key_pattern)
            quiz_votes = []

            for user_key in user_keys:
                answer_data_json = await connection.get(user_key)
                answer_data = json.loads(answer_data_json)
                quiz_votes.append(answer_data)

            quiz_votes = [UserQuizVote.model_validate(quiz, from_attributes=True) for quiz in quiz_votes]

            return quiz_votes

        except Exception as e:
            raise e

