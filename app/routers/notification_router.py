from fastapi import APIRouter, Depends

from schemas.notification_schema import NotificationListResponseWithPagination
from services.notification_service import NotificationService

router = APIRouter()


@router.get("/my_notifications", response_model=NotificationListResponseWithPagination)
async def get_all_my_notifications(skip: int = 0, limit: int = 5,
                                   service: NotificationService = Depends()) -> NotificationListResponseWithPagination:
    notifications = await service.get_my_notifications(skip=skip, limit=limit)
    return notifications


@router.get("/my_notifications/{notif_id}")
async def read_notification_by_id(notif_id: int, service: NotificationService = Depends()):
    notification = await service.get_notification_by_id(notif_id=notif_id)
    return notification
