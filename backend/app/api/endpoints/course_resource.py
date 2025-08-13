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
)
from app.utils.response import Success, NotFound, BadRequest

router = APIRouter()


@router.post("/")
def create_course_resource(
    *,
    db: Session = Depends(deps.get_mysql_db),
    resource_in: CourseResourceCreate,
    current_user: User = Depends(deps.get_current_user),
):
    """
    Create new course resource.
    """
    existing_resource = crud_course_resource.get_by_name(db=db, name=resource_in.name)
    if existing_resource:
        return BadRequest(message="Course resource with this name already exists.")
        
    resource = crud_course_resource.create_course_resource(db=db, resource_in=resource_in, creator_id=current_user.id)
    return Success(data=CourseResourceResponse.from_orm(resource).model_dump())


@router.get("/")
def read_course_resources(
    db: Session = Depends(deps.get_mysql_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    name: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
):
    """
    Retrieve course resources with pagination and filtering.
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
    db: Session = Depends(deps.get_mysql_db),
    uuid: str,
):
    """
    Get course resource by UUID.
    """
    resource = crud_course_resource.get_course_resource_by_uuid(db=db, uuid=uuid)
    if not resource:
        return NotFound(message="Course resource not found")
    return Success(data=CourseResourceResponse.from_orm(resource).model_dump())


@router.put("/{uuid}")
def update_course_resource(
    *,
    db: Session = Depends(deps.get_mysql_db),
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
    db: Session = Depends(deps.get_mysql_db),
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
