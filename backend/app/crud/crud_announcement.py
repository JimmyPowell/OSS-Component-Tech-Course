from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, Tuple
from datetime import datetime
import uuid

from app.models.announcement import Announcement
from app.schemas.announcement import AnnouncementCreate, AnnouncementUpdate


def create_announcement(db: Session, *, announcement_in: AnnouncementCreate, publisher_id: int) -> Announcement:
    db_obj = Announcement(**announcement_in.dict(exclude={"uuid"}), uuid=str(uuid.uuid4()), publisher_id=publisher_id)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_announcement_by_uuid(db: Session, *, uuid: str) -> Optional[Announcement]:
    return db.query(Announcement).filter(Announcement.uuid == uuid, Announcement.deleted_at.is_(None)).first()


def get_by_name(db: Session, *, name: str) -> Optional[Announcement]:
    return db.query(Announcement).filter(Announcement.name == name, Announcement.deleted_at.is_(None)).first()


def get_multi(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 10,
    name: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
) -> Tuple[int, list[Announcement]]:
    query = db.query(Announcement).filter(Announcement.deleted_at.is_(None))

    filters = []
    if name:
        filters.append(Announcement.name.ilike(f"%{name}%"))
    if start_time:
        filters.append(Announcement.created_at >= start_time)
    if end_time:
        filters.append(Announcement.created_at <= end_time)

    if filters:
        query = query.filter(and_(*filters))

    total = query.count()
    items = query.order_by(Announcement.created_at.desc()).offset(skip).limit(limit).all()

    return total, items


def update_announcement(db: Session, *, db_obj: Announcement, obj_in: AnnouncementUpdate) -> Announcement:
    update_data = obj_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def remove_announcement(db: Session, *, db_obj: Announcement) -> Announcement:
    db_obj.deleted_at = datetime.utcnow()
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj