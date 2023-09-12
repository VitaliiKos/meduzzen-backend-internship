from typing import List

from pydantic import BaseModel
from datetime import datetime


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    quiz_id: int
    massage: str
    is_read: bool
    created_at: datetime


class NotificationListResponseWithPagination(BaseModel):
    total_item: int
    total_page: int
    data: List[NotificationResponse]

    class Config:
        from_attributes = True
