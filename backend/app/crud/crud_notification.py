import uuid
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func

from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationCreate, NotificationUpdate


class CRUDNotification:
    
    def create_notification(self, db: Session, *, notification_in: NotificationCreate) -> Notification:
        """创建通知"""
        db_obj = Notification(
            uuid=str(uuid.uuid4()),
            recipient_id=notification_in.recipient_id,
            sender_id=notification_in.sender_id,
            admin_id=notification_in.admin_id,
            type=notification_in.type,
            title=notification_in.title,
            content=notification_in.content,
            related_id=notification_in.related_id,
            related_uuid=notification_in.related_uuid
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_notification_by_uuid(self, db: Session, *, uuid: str) -> Optional[Notification]:
        """根据UUID获取通知"""
        return db.query(Notification).options(
            joinedload(Notification.sender),
            joinedload(Notification.admin)
        ).filter(Notification.uuid == uuid).first()
    
    def get_user_notifications(self, db: Session, *, user_id: int, skip: int = 0, limit: int = 20) -> Tuple[int, int, List[Notification]]:
        """获取用户的通知列表"""
        query = db.query(Notification).options(
            joinedload(Notification.sender),
            joinedload(Notification.admin)
        ).filter(Notification.recipient_id == user_id)
        
        total = query.count()
        unread_count = query.filter(Notification.is_read == False).count()
        
        notifications = query.order_by(desc(Notification.created_at)).offset(skip).limit(limit).all()
        
        return total, unread_count, notifications
    
    def update_notification(self, db: Session, *, db_obj: Notification, obj_in: NotificationUpdate) -> Notification:
        """更新通知"""
        update_data = obj_in.model_dump(exclude_unset=True)
        
        if update_data.get("is_read") is True and not db_obj.is_read:
            # 设置阅读时间
            update_data["read_at"] = func.now()
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def mark_notification_as_read(self, db: Session, *, notification_uuid: str, user_id: int) -> Optional[Notification]:
        """标记通知为已读"""
        notification = db.query(Notification).filter(
            Notification.uuid == notification_uuid,
            Notification.recipient_id == user_id
        ).first()
        
        if notification and not notification.is_read:
            notification.is_read = True
            notification.read_at = func.now()
            db.add(notification)
            db.commit()
            db.refresh(notification)
        
        return notification
    
    def mark_all_notifications_as_read(self, db: Session, *, user_id: int) -> int:
        """标记用户所有通知为已读"""
        count = db.query(Notification).filter(
            Notification.recipient_id == user_id,
            Notification.is_read == False
        ).update({
            Notification.is_read: True,
            Notification.read_at: func.now()
        })
        db.commit()
        return count
    
    def delete_notification(self, db: Session, *, db_obj: Notification) -> Notification:
        """删除通知"""
        db.delete(db_obj)
        db.commit()
        return db_obj
    
    def get_unread_count(self, db: Session, *, user_id: int) -> int:
        """获取用户未读通知数量"""
        return db.query(Notification).filter(
            Notification.recipient_id == user_id,
            Notification.is_read == False
        ).count()


# 实例化CRUD对象
crud_notification = CRUDNotification()