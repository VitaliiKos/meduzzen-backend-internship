from typing import List

from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, BOOLEAN, Float
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Employee(Base):
    __tablename__ = "employee_table"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_table.id"))
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("company_table.id"))
    role = Column(String, nullable=False)

    invitation_status = Column(String)  # Invitation status (accepted, rejected, pending)
    request_status = Column(String)  # Membership request status (accepted, rejected, pending)
    created_at = Column(DateTime)  # Date the invitation was sent

    # association between Employee -> Company
    firm: Mapped["Company"] = relationship("Company", back_populates="user_employees")

    # association between Employee -> User
    worker: Mapped["User"] = relationship("User", back_populates="company_employees")


class User(Base):
    __tablename__ = 'user_table'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, nullable=True)
    password = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    city = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=func.now(), nullable=False)

    # many-to-many relationship to Employee, bypassing the `Employee` class
    companies: Mapped[List['Company']] = relationship("Company", secondary='employee_table',
                                                      back_populates="users", overlaps="firm")
    # association between User -> Employee -> Company
    company_employees: Mapped[List["Employee"]] = relationship("Employee", back_populates="worker")
    quiz_results: Mapped[List['QuizResult']] = relationship("QuizResult", back_populates="user")


class Company(Base):
    __tablename__ = 'company_table'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    phone = Column(String, nullable=False)
    email = Column(String, nullable=False)
    status = Column(BOOLEAN, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=func.now(), nullable=False)

    # many-to-many relationship to Parent, bypassing the `Association` class
    users: Mapped[List["User"]] = relationship("User", secondary="employee_table", back_populates="companies",
                                               overlaps="firm")

    # association between Child -> Association -> Parent
    user_employees: Mapped[List["Employee"]] = relationship("Employee", back_populates="firm",
                                                            overlaps="companies,users")

    # Relationship to quizzes
    quizzes: Mapped[List["Quiz"]] = relationship("Quiz", back_populates="company")


class Quiz(Base):
    __tablename__ = 'quiz_table'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("company_table.id"))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_table.id"))
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    frequency_in_days = Column(Integer, nullable=False)
    is_deleted = Column(BOOLEAN, default=False)

    # Relationship to questions
    questions: Mapped[List['Question']] = relationship("Question", cascade="all", back_populates="quiz")
    company: Mapped["Company"] = relationship("Company", back_populates="quizzes")

    quiz_results: Mapped[List['QuizResult']] = relationship("QuizResult", back_populates="quiz")


class Question(Base):
    __tablename__ = 'question_table'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    quiz_id: Mapped[int] = mapped_column(Integer, ForeignKey("quiz_table.id"))
    question_text = Column(String, nullable=False)

    # Relationship to answers
    answers: Mapped[List['Answer']] = relationship("Answer", cascade="all", back_populates="question")
    quiz: Mapped["Quiz"] = relationship("Quiz", back_populates="questions")


class Answer(Base):
    __tablename__ = 'answer_table'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("question_table.id"))
    answer_text = Column(String, nullable=False)
    is_correct = Column(BOOLEAN, default=False)
    question: Mapped["Question"] = relationship("Question", back_populates="answers")


class QuizResult(Base):
    __tablename__ = 'quiz_result_table'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_table.id", ondelete="CASCADE"))
    quiz_id: Mapped[int] = mapped_column(Integer, ForeignKey("quiz_table.id"))
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("company_table.id"))
    total_question = Column(Integer, default=0)
    total_answers = Column(Integer, default=0)
    score = Column(Float, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    user = relationship("User", back_populates="quiz_results")
    quiz = relationship("Quiz", back_populates="quiz_results")


class Notification(Base):
    __tablename__ = 'notification_table'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_table.id", ondelete="CASCADE"))
    quiz_id: Mapped[int] = mapped_column(Integer, ForeignKey("quiz_table.id", ondelete="CASCADE"))
    massage = Column(String, nullable=False)
    is_read = Column(BOOLEAN, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
