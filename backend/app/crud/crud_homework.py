from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, Tuple
from datetime import datetime
import uuid

from app.models.homework import Homework
from app.models.user import User
from app.schemas.homework import HomeworkCreate, HomeworkUpdate


def create_homework(db: Session, *, homework_in: HomeworkCreate, creator_id: int) -> Homework:
    db_obj = Homework(**homework_in.dict(exclude={"uuid"}), uuid=str(uuid.uuid4()), creator_id=creator_id)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_homework_by_uuid(db: Session, *, uuid: str) -> Optional[Homework]:
    return db.query(Homework).filter(Homework.uuid == uuid, Homework.deleted_at.is_(None)).first()


def get_homework_detail_by_uuid(db: Session, *, uuid: str) -> Optional[dict]:
    """Get homework with publisher information by UUID"""
    result = db.query(
        Homework,
        User.username,
        User.avatar_url
    ).join(
        User, Homework.creator_id == User.id
    ).filter(
        Homework.uuid == uuid,
        Homework.deleted_at.is_(None)
    ).first()
    
    if not result:
        return None
        
    homework, publisher_name, publisher_avatar = result
    
    # Convert to dict and add publisher info
    homework_dict = {
        "uuid": homework.uuid,
        "name": homework.name,
        "description": homework.description,
        "content": homework.content,
        "cover_url": homework.cover_url,
        "resource_urls": homework.resource_urls,
        "lasting_time": homework.lasting_time,
        "creator_id": homework.creator_id,
        "publisher_name": publisher_name,
        "publisher_avatar": publisher_avatar,
        "created_at": homework.created_at,
        "updated_at": homework.updated_at,
    }
    
    return homework_dict


def get_by_name(db: Session, *, name: str) -> Optional[Homework]:
    return db.query(Homework).filter(Homework.name == name, Homework.deleted_at.is_(None)).first()


def get_multi(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 10,
    name: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
) -> Tuple[int, list[Homework]]:
    query = db.query(Homework).filter(Homework.deleted_at.is_(None))

    filters = []
    if name:
        filters.append(Homework.name.ilike(f"%{name}%"))
    if start_time:
        filters.append(Homework.created_at >= start_time)
    if end_time:
        filters.append(Homework.created_at <= end_time)

    if filters:
        query = query.filter(and_(*filters))

    total = query.count()
    items = query.offset(skip).limit(limit).all()

    return total, items


def update_homework(db: Session, *, db_obj: Homework, obj_in: HomeworkUpdate) -> Homework:
    update_data = obj_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def remove_homework(db: Session, *, db_obj: Homework) -> Homework:
    db_obj.deleted_at = datetime.utcnow()
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
