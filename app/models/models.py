# from datetime import datetime
# from sqlalchemy import Column, Integer, String, MetaData, TIMESTAMP
#
# from app.db.database import Base
#
# metadata = MetaData()
#
#
# class UserDB(Base):
#     __tablename__ = "users"
#
#     user_id = Column(Integer, primary_key=True, index=True)
#     firstname = Column(String)
#     lastname = Column(String)
#     phone_number = Column(String, unique=True)
#     age = Column(Integer)
#     city = Column(Integer)
#     created_at = Column(TIMESTAMP, nullable=False, datetime=datetime.utcnow)
#
# # roles = Table(
# #     "roles",
# #     metadata,
# #     Column("id", Integer, primary_key=True),
# #     Column("name", String, nullable=False),
# #     Column("permission", JSON)
# # )
# #
# # users = Table(
# #     "users",
# #     Column("id", Integer, primary_key=True, index=True),
# #     Column("email",String, unique=True, index=True, nullable=False),
# #     Column("username",String, index=True, nullable=False),
# #     Column("hashed_password", String, nullable=False),
# #     Column("city", String, default=True),
# #     Column("is_active", Boolean, default=True),
# #     Column("created_at", TIMESTAMP, nullable=False, datetime=datetime.utcnow),
# #     relationship("role_id", ForeignKey("roles_id")),
# # )
#
# # from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
# # from sqlalchemy.orm import relationship
# #
# # from app.db.database import Base
# #
# #
# # class User(Base):
# #     __tablename__ = "users"
# #
# #     id = Column(Integer, primary_key=True, index=True)
# #     email = Column(String, unique=True, index=True)
# #     hashed_password = Column(String)
# #     is_active = Column(Boolean, default=True)
# #
# #     items = relationship("Item", back_populates="owner")
# #
# #
# # class Item(Base):
# #     __tablename__ = "items"
# #
# #     id = Column(Integer, primary_key=True, index=True)
# #     title = Column(String, index=True)
# #     description = Column(String, index=True)
# #     owner_id = Column(Integer, ForeignKey("users.id"))
# #
# #     owner = relationship("User", back_populates="items")
