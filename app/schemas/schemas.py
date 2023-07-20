# from pydantic import BaseModel
#
#
# class UserBase(BaseModel):
#     firstname: str
#     lastname: str
#     phone_number: str
#     age: int
#     city: str
#
#     class Config:
#         orm_mode = True
#
#
# class UserCreate(UserBase):
#     password: str
# #
# #
# # class User(UserBase):
# #     id: int
# #     is_active: bool
# #     items: list[Item] = []
# #
# #     class Config:
# #         orm_mode = True
#
# #
# # class ItemBase(BaseModel):
# #     title: str
# #     description: str | None = None
# #
# #
# # class ItemCreate(ItemBase):
# #     pass
# #
# #
# # class Item(ItemBase):
# #     id: int
# #     owner_id: int
# #
# #     class Config:
# #         orm_mode = True
# #
# #
