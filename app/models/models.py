from typing import List

from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, BOOLEAN
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
    companies: Mapped[List['Company']] = relationship("Company", secondary='employee_table', back_populates="users"
                                                      )
    # association between User -> Employee -> Company
    company_employees: Mapped[List["Employee"]] = relationship("Employee", back_populates="worker")


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
    users: Mapped[List["User"]] = relationship("User", secondary="employee_table", back_populates="companies")

    # association between Child -> Association -> Parent
    user_employees: Mapped[List["Employee"]] = relationship("Employee", back_populates="firm")
