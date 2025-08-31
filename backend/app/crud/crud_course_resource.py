from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Optional, Tuple
from datetime import datetime
import uuid

from app.models.course_resource import CourseResource
from app.models.user import User
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


def get_by_name_and_type(db: Session, *, name: str, resource_type: str) -> Optional[CourseResource]:
    """
    检查同类型下是否存在同名资源
    """
    return db.query(CourseResource).filter(
        CourseResource.name == name,
        CourseResource.type == resource_type,
        CourseResource.deleted_at.is_(None)
    ).first()


def get_multi(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 10,
    name: Optional[str] = None,
    resource_type: Optional[str] = None,
    status: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
) -> Tuple[int, list[CourseResource]]:
    query = db.query(CourseResource).filter(CourseResource.deleted_at.is_(None))

    filters = []
    if name:
        filters.append(CourseResource.name.ilike(f"%{name}%"))
    if resource_type:
        filters.append(CourseResource.type == resource_type)
    if status:
        filters.append(CourseResource.status == status)
    if start_time:
        filters.append(CourseResource.created_at >= start_time)
    if end_time:
        filters.append(CourseResource.created_at <= end_time)

    if filters:
        query = query.filter(and_(*filters))

    total = query.count()
    items = query.order_by(CourseResource.created_at.desc()).offset(skip).limit(limit).all()

    return total, items


def get_published(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 10,
    name: Optional[str] = None,
    resource_type: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
) -> Tuple[int, list[CourseResource]]:
    """获取已发布的课程资源（普通用户访问）"""
    return get_multi(
        db,
        skip=skip,
        limit=limit,
        name=name,
        resource_type=resource_type,
        status="published",
        start_time=start_time,
        end_time=end_time
    )


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


def get_course_resource_detail_by_uuid(db: Session, *, uuid: str, status_filter: Optional[str] = None) -> Optional[dict]:
    """
    获取课程资源详情，包含发布者信息
    返回包含课程资源和用户信息的字典
    """
    query = db.query(CourseResource, User).join(
        User, CourseResource.creator_id == User.id
    ).filter(
        CourseResource.uuid == uuid,
        CourseResource.deleted_at.is_(None),
        User.deleted_at.is_(None)
    )
    
    # 如果指定状态过滤，只返回指定状态的资源
    if status_filter:
        query = query.filter(CourseResource.status == status_filter)
    
    result = query.first()
    
    if not result:
        return None
    
    resource, user = result
    
    return {
        'uuid': resource.uuid,
        'name': resource.name,
        'type': resource.type,
        'description': resource.description,
        'cover_url': resource.cover_url,
        'resource_url': resource.resource_url,
        'file_size': resource.file_size,
        'mime_type': resource.mime_type,
        'status': resource.status,
        'download_count': resource.download_count,
        'created_at': resource.created_at,
        'updated_at': resource.updated_at,
        'publisher_id': user.id,
        'publisher_name': user.username or user.real_name,
        'publisher_avatar': user.avatar_url
    }


def update_status(db: Session, *, db_obj: CourseResource, status: str) -> CourseResource:
    """更新课程资源状态"""
    db_obj.status = status
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_course_resource_by_uuid_published(db: Session, *, uuid: str) -> Optional[CourseResource]:
    """获取已发布的课程资源（普通用户访问）"""
    return db.query(CourseResource).filter(
        CourseResource.uuid == uuid,
        CourseResource.status == "published",
        CourseResource.deleted_at.is_(None)
    ).first()
