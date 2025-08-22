from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.api import deps
from app.crud import crud_announcement
from app.models import User
from app.schemas.announcement import (
    AnnouncementCreate,
    AnnouncementUpdate,
    AnnouncementResponse,
)
from app.utils.response import Success, NotFound, BadRequest

router = APIRouter()

# 管理员路由
admin_router = APIRouter()


# 管理员创建公告端点
@admin_router.post("/")
def create_announcement_admin(
    *,
    db: Session = Depends(deps.get_db),
    announcement_in: AnnouncementCreate,
    current_user: User = Depends(deps.get_current_manager_user),
):
    """
    Create new announcement (Admin only).
    """
    existing_announcement = crud_announcement.get_by_name(db=db, name=announcement_in.name)
    if existing_announcement:
        return BadRequest(message="Announcement with this name already exists.")
        
    announcement = crud_announcement.create_announcement(db=db, announcement_in=announcement_in, publisher_id=current_user.id)
    return Success(data=AnnouncementResponse.from_orm(announcement).model_dump())

@router.post("/")
def create_announcement(
    *,
    db: Session = Depends(deps.get_db),
    announcement_in: AnnouncementCreate,
    current_user: User = Depends(deps.get_current_user),
):
    """
    Create new announcement.
    """
    existing_announcement = crud_announcement.get_by_name(db=db, name=announcement_in.name)
    if existing_announcement:
        return BadRequest(message="Announcement with this name already exists.")
        
    announcement = crud_announcement.create_announcement(db=db, announcement_in=announcement_in, publisher_id=current_user.id)
    return Success(data=AnnouncementResponse.from_orm(announcement).model_dump())


# 管理员查看公告端点
@admin_router.get("/")
def read_announcements_admin(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_manager_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    name: Optional[str] = Query(None),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
):
    """
    Retrieve announcements with pagination and filtering (Admin only).
    """
    total, announcements = crud_announcement.get_multi(
        db,
        skip=skip,
        limit=limit,
        name=name,
        start_time=start_time,
        end_time=end_time,
    )
    return Success(data={"total": total, "items": [AnnouncementResponse.from_orm(a).model_dump() for a in announcements]})

@router.get("/")
def read_announcements(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    name: Optional[str] = Query(None),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
):
    """
    Retrieve announcements with pagination and filtering.
    """
    total, announcements = crud_announcement.get_multi(
        db,
        skip=skip,
        limit=limit,
        name=name,
        start_time=start_time,
        end_time=end_time,
    )
    return Success(data={"total": total, "items": [AnnouncementResponse.from_orm(a).model_dump() for a in announcements]})


# 管理员查看单个公告端点
@admin_router.get("/{uuid}")
def read_announcement_admin(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
    current_user: User = Depends(deps.get_current_manager_user),
):
    """
    Get announcement by UUID (Admin only).
    """
    announcement = crud_announcement.get_announcement_by_uuid(db=db, uuid=uuid)
    if not announcement:
        return NotFound(message="Announcement not found")
    return Success(data=AnnouncementResponse.from_orm(announcement).model_dump())

@router.get("/{uuid}")
def read_announcement(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
):
    """
    Get announcement by UUID.
    """
    announcement = crud_announcement.get_announcement_by_uuid(db=db, uuid=uuid)
    if not announcement:
        return NotFound(message="Announcement not found")
    return Success(data=AnnouncementResponse.from_orm(announcement).model_dump())


# 管理员更新公告端点
@admin_router.put("/{uuid}")
def update_announcement_admin(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
    announcement_in: AnnouncementUpdate,
    current_user: User = Depends(deps.get_current_manager_user),
):
    """
    Update an announcement (Admin only).
    """
    announcement = crud_announcement.get_announcement_by_uuid(db=db, uuid=uuid)
    if not announcement:
        return NotFound(message="Announcement not found")
    announcement = crud_announcement.update_announcement(db=db, db_obj=announcement, obj_in=announcement_in)
    return Success(data=AnnouncementResponse.from_orm(announcement).model_dump())

@router.put("/{uuid}")
def update_announcement(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
    announcement_in: AnnouncementUpdate,
):
    """
    Update an announcement.
    """
    announcement = crud_announcement.get_announcement_by_uuid(db=db, uuid=uuid)
    if not announcement:
        return NotFound(message="Announcement not found")
    announcement = crud_announcement.update_announcement(db=db, db_obj=announcement, obj_in=announcement_in)
    return Success(data=AnnouncementResponse.from_orm(announcement).model_dump())


# 管理员删除公告端点
@admin_router.delete("/{uuid}")
def delete_announcement_admin(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
    current_user: User = Depends(deps.get_current_manager_user),
):
    """
    Delete an announcement (Admin only).
    """
    announcement = crud_announcement.get_announcement_by_uuid(db=db, uuid=uuid)
    if not announcement:
        return NotFound(message="Announcement not found")
    announcement = crud_announcement.remove_announcement(db=db, db_obj=announcement)
    return Success(data=AnnouncementResponse.from_orm(announcement).model_dump())

@router.delete("/{uuid}")
def delete_announcement(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
):
    """
    Delete an announcement.
    """
    announcement = crud_announcement.get_announcement_by_uuid(db=db, uuid=uuid)
    if not announcement:
        return NotFound(message="Announcement not found")
    announcement = crud_announcement.remove_announcement(db=db, db_obj=announcement)
    return Success(data=AnnouncementResponse.from_orm(announcement).model_dump())