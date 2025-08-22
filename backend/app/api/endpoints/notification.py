from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.api import deps
from app.crud.crud_notification import crud_notification
from app.models import User
from app.schemas.notification import (
    NotificationCreate,
    NotificationUpdate,
    NotificationResponse,
    PaginatedNotificationResponse,
    NotificationMarkAllReadRequest
)
from app.utils.response import Success, NotFound, Forbidden

router = APIRouter()

# 管理员路由
admin_router = APIRouter()


@router.get("/", response_model=dict)
def read_notifications(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """
    获取当前用户的通知列表
    """
    total, unread_count, notifications = crud_notification.get_user_notifications(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    
    response_data = PaginatedNotificationResponse(
        total=total,
        unread_count=unread_count,
        items=[NotificationResponse.from_orm(n).model_dump() for n in notifications]
    )
    
    return Success(data=response_data.model_dump())


@router.get("/unread-count", response_model=dict)
def get_unread_count(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    获取当前用户未读通知数量
    """
    count = crud_notification.get_unread_count(db, user_id=current_user.id)
    return Success(data={"unread_count": count})


@router.get("/{uuid}", response_model=dict)
def read_notification(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
    current_user: User = Depends(deps.get_current_user),
):
    """
    获取通知详情
    """
    notification = crud_notification.get_notification_by_uuid(db=db, uuid=uuid)
    if not notification:
        return NotFound(message="Notification not found")
    
    # 检查权限
    if notification.recipient_id != current_user.id:
        return Forbidden(message="Not enough permissions")
    
    return Success(data=NotificationResponse.from_orm(notification).model_dump())


@router.put("/{uuid}/read", response_model=dict)
def mark_notification_as_read(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
    current_user: User = Depends(deps.get_current_user),
):
    """
    标记通知为已读
    """
    notification = crud_notification.mark_notification_as_read(
        db=db, notification_uuid=uuid, user_id=current_user.id
    )
    
    if not notification:
        return NotFound(message="Notification not found")
    
    return Success(data={"message": "Notification marked as read"})


@router.put("/mark-all-read", response_model=dict)
def mark_all_notifications_as_read(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    标记所有通知为已读
    """
    count = crud_notification.mark_all_notifications_as_read(db=db, user_id=current_user.id)
    return Success(data={"message": f"Marked {count} notifications as read"})


@router.delete("/{uuid}", response_model=dict)
def delete_notification(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
    current_user: User = Depends(deps.get_current_user),
):
    """
    删除通知
    """
    notification = crud_notification.get_notification_by_uuid(db=db, uuid=uuid)
    if not notification:
        return NotFound(message="Notification not found")
    
    # 检查权限
    if notification.recipient_id != current_user.id:
        return Forbidden(message="Not enough permissions")
    
    crud_notification.delete_notification(db=db, db_obj=notification)
    return Success(data={"message": "Notification deleted"})


# 管理员API - 创建系统通知
@admin_router.post("/", response_model=dict)
def create_notification_admin(
    *,
    db: Session = Depends(deps.get_db),
    notification_in: NotificationCreate,
    current_user: User = Depends(deps.get_current_manager_user),
):
    """
    创建通知（管理员）
    """
    # 设置管理员ID
    notification_in.admin_id = current_user.id
    
    notification = crud_notification.create_notification(db=db, notification_in=notification_in)
    return Success(data=NotificationResponse.from_orm(notification).model_dump())


@admin_router.post("/broadcast", response_model=dict)
def broadcast_notification(
    *,
    db: Session = Depends(deps.get_db),
    title: str,
    content: Optional[str] = None,
    current_user: User = Depends(deps.get_current_manager_user),
):
    """
    广播通知给所有用户（管理员）
    """
    from app.models.user import User as UserModel
    
    # 获取所有活跃用户
    users = db.query(UserModel).filter(UserModel.is_active == True).all()
    
    created_count = 0
    for user in users:
        notification_in = NotificationCreate(
            recipient_id=user.id,
            admin_id=current_user.id,
            type="system_announcement",
            title=title,
            content=content
        )
        crud_notification.create_notification(db=db, notification_in=notification_in)
        created_count += 1
    
    return Success(data={"message": f"Broadcast notification sent to {created_count} users"})