import math

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from db.database import get_session, async_session
from models.models import User as UserModel, Company as CompanyModel, Notification as NotificationModel, \
    Employee as EmployeeModel
from schemas.notification_schema import NotificationResponse, NotificationListResponseWithPagination
from services.auth import authenticate_and_get_user
from sqlalchemy import select
from datetime import datetime
from fastapi import HTTPException, status


class NotificationService:
    def __init__(self, session: AsyncSession = Depends(get_session),
                 user: UserModel = Depends(authenticate_and_get_user)):
        self.session = session
        self.user = user

    async def get_my_notifications(self, skip: int, limit: int) -> NotificationListResponseWithPagination:
        stmt = select(NotificationModel).where(NotificationModel.user_id == self.user.id).offset(skip).limit(limit)
        notification_list = await self.session.execute(stmt)

        my_notification = [NotificationResponse.model_validate(item, from_attributes=True) for item in
                           notification_list.scalars()]

        result2_for_pagination = await self.session.execute(
            select(NotificationModel).where(NotificationModel.user_id == self.user.id))
        total_item = len(result2_for_pagination.all())
        total_page = math.ceil(math.ceil(total_item / limit))

        return NotificationListResponseWithPagination(data=my_notification, total_item=total_item,
                                                      total_page=total_page)

    async def get_notification_by_id(self, notif_id: int):
        existing_notification = await self.session.get(NotificationModel, notif_id)

        if not existing_notification or (existing_notification.user_id != self.user.id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

        existing_notification.is_read = True
        await self.session.commit()

        print(existing_notification.__dict__)

    @staticmethod
    async def create_notification(company_id: int, quiz_id: int, quiz_title: str):
        async with async_session() as session:
            stmt = select(UserModel).join(EmployeeModel, EmployeeModel.company_id == company_id).where(
                UserModel.id == EmployeeModel.user_id, EmployeeModel.__table__.c.role != 'Candidate')
            members = await session.execute(stmt)

            for member in members.scalars():
                new_notification = NotificationModel(user_id=member.id, quiz_id=quiz_id,
                                                     massage=f'New quiz "{quiz_title}" is available!')
                new_notification.is_read = False
                new_notification.created_at = datetime.utcnow()
                session.add(new_notification)
                await session.commit()
