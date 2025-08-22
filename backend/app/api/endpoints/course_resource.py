from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.api import deps
from app.crud import crud_course_resource
from app.models import User
from app.schemas.course_resource import (
    CourseResourceCreate,
    CourseResourceUpdate,
    CourseResourceResponse,
    PaginatedCourseResourceResponse,
    CourseResourceDetailResponse,
)
from app.utils.response import Success, NotFound, BadRequest

router = APIRouter()


@router.post("/")
def create_course_resource(
    *,
    db: Session = Depends(deps.get_db),
    resource_in: CourseResourceCreate,
    current_user: dict = Depends(deps.get_current_manager_user),
):
    """
    Create new course resource. Requires manager role.
    """
    existing_resource = crud_course_resource.get_by_name(db=db, name=resource_in.name)
    if existing_resource:
        return BadRequest(message="Course resource with this name already exists.")
    
    # Get user ID from database using UUID (only for create operations where we need the ID)
    from app.crud import crud_user
    user = crud_user.get_user_by_uuid(db=db, uuid=current_user["uuid"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    resource = crud_course_resource.create_course_resource(db=db, resource_in=resource_in, creator_id=user.id)
    return Success(data=CourseResourceResponse.from_orm(resource).model_dump())


@router.get("/")
def read_course_resources(
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    name: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
):
    """
    Retrieve course resources with pagination and filtering.
    Requires authentication.
    """
    total, resources = crud_course_resource.get_multi(
        db,
        skip=skip,
        limit=limit,
        name=name,
        resource_type=resource_type,
        start_time=start_time,
        end_time=end_time,
    )
    return Success(data={"total": total, "items": [CourseResourceResponse.from_orm(r).model_dump() for r in resources]})


@router.get("/{uuid}")
def read_course_resource(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
    current_user: dict = Depends(deps.get_current_user),
):
    """
    Get course resource by UUID.
    Requires authentication.
    """
    resource = crud_course_resource.get_course_resource_by_uuid(db=db, uuid=uuid)
    if not resource:
        return NotFound(message="Course resource not found")
    return Success(data=CourseResourceResponse.from_orm(resource).model_dump())


@router.get("/{uuid}/detail")
def read_course_resource_detail(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
    current_user: dict = Depends(deps.get_current_user),
):
    """
    Get course resource detail with publisher information by UUID.
    Requires authentication.
    """
    resource_detail = crud_course_resource.get_course_resource_detail_by_uuid(db=db, uuid=uuid)
    if not resource_detail:
        return NotFound(message="Course resource not found")
    return Success(data=resource_detail)


@router.put("/{uuid}")
def update_course_resource(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
    resource_in: CourseResourceUpdate,
):
    """
    Update a course resource.
    """
    resource = crud_course_resource.get_course_resource_by_uuid(db=db, uuid=uuid)
    if not resource:
        return NotFound(message="Course resource not found")
    resource = crud_course_resource.update_course_resource(db=db, db_obj=resource, obj_in=resource_in)
    return Success(data=CourseResourceResponse.from_orm(resource).model_dump())


@router.delete("/{uuid}")
def delete_course_resource(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
):
    """
    Delete a course resource.
    """
    resource = crud_course_resource.get_course_resource_by_uuid(db=db, uuid=uuid)
    if not resource:
        return NotFound(message="Course resource not found")
    resource = crud_course_resource.remove_course_resource(db=db, db_obj=resource)
    return Success(data=CourseResourceResponse.from_orm(resource).model_dump())


@router.post("/{uuid}/increment-view")
def increment_view_count(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
    current_user: dict = Depends(deps.get_current_user),
):
    """
    Increment view count for a course resource.
    Requires authentication.
    """
    resource = crud_course_resource.get_course_resource_by_uuid(db=db, uuid=uuid)
    if not resource:
        return NotFound(message="Course resource not found")
    
    # 增加播放次数
    resource.download_count += 1
    db.commit()
    db.refresh(resource)
    
    return Success(data={"download_count": resource.download_count, "message": "View count updated"})
