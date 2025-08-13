from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Optional, Tuple
from datetime import datetime
import uuid

from app.models.course_resource import CourseResource
from app.schemas.course_resource import CourseResourceCreate, CourseResourceUpdate


def create_course_resource(db: Session, *, resource_in: CourseResourceCreate, creator_id: int) -> CourseResource:
    db_obj = CourseResource(**resource_in.dict(exclude={"uuid"}), uuid=str(uuid.uuid4()), creator_id=creator_id)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_course_resource_by_uuid(db: Session, *, uuid: str) -> Optional[CourseResource]:
    return db.query(CourseResource).filter(CourseResource.uuid == uuid, CourseResource.deleted_at.is_(None)).first()


def get_by_name(db: Session, *, name: str) -> Optional[CourseResource]:
    return db.query(CourseResource).filter(CourseResource.name == name, CourseResource.deleted_at.is_(None)).first()


def get_multi(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 10,
    name: Optional[str] = None,
    resource_type: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
) -> Tuple[int, list[CourseResource]]:
    query = db.query(CourseResource).filter(CourseResource.deleted_at.is_(None))

    filters = []
    if name:
        filters.append(CourseResource.name.ilike(f"%{name}%"))
    if resource_type:
        filters.append(CourseResource.type == resource_type)
    if start_time:
        filters.append(CourseResource.created_at >= start_time)
    if end_time:
        filters.append(CourseResource.created_at <= end_time)

    if filters:
        query = query.filter(and_(*filters))

    total = query.count()
    items = query.offset(skip).limit(limit).all()

    return total, items


def update_course_resource(db: Session, *, db_obj: CourseResource, obj_in: CourseResourceUpdate) -> CourseResource:
    update_data = obj_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def remove_course_resource(db: Session, *, db_obj: CourseResource) -> CourseResource:
    db_obj.deleted_at = datetime.utcnow()
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
