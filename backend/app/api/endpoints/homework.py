from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.api import deps
from app.crud import crud_homework
from app.models import User
from app.schemas.homework import (
    HomeworkCreate,
    HomeworkUpdate,
    HomeworkResponse,
)
from app.utils.response import Success, NotFound, BadRequest

router = APIRouter()


@router.post("/")
def create_homework(
    *,
    db: Session = Depends(deps.get_mysql_db),
    homework_in: HomeworkCreate,
    current_user: User = Depends(deps.get_current_user),
):
    """
    Create new homework.
    """
    existing_homework = crud_homework.get_by_name(db=db, name=homework_in.name)
    if existing_homework:
        return BadRequest(message="Homework with this name already exists.")
        
    homework = crud_homework.create_homework(db=db, homework_in=homework_in, creator_id=current_user.id)
    return Success(data=HomeworkResponse.from_orm(homework).model_dump())


@router.get("/")
def read_homeworks(
    db: Session = Depends(deps.get_mysql_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    name: Optional[str] = Query(None),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
):
    """
    Retrieve homeworks with pagination and filtering.
    """
    total, homeworks = crud_homework.get_multi(
        db,
        skip=skip,
        limit=limit,
        name=name,
        start_time=start_time,
        end_time=end_time,
    )
    return Success(data={"total": total, "items": [HomeworkResponse.from_orm(h).model_dump() for h in homeworks]})


@router.get("/{uuid}")
def read_homework(
    *,
    db: Session = Depends(deps.get_mysql_db),
    uuid: str,
):
    """
    Get homework by UUID.
    """
    homework = crud_homework.get_homework_by_uuid(db=db, uuid=uuid)
    if not homework:
        return NotFound(message="Homework not found")
    return Success(data=HomeworkResponse.from_orm(homework).model_dump())


@router.put("/{uuid}")
def update_homework(
    *,
    db: Session = Depends(deps.get_mysql_db),
    uuid: str,
    homework_in: HomeworkUpdate,
):
    """
    Update a homework.
    """
    homework = crud_homework.get_homework_by_uuid(db=db, uuid=uuid)
    if not homework:
        return NotFound(message="Homework not found")
    homework = crud_homework.update_homework(db=db, db_obj=homework, obj_in=homework_in)
    return Success(data=HomeworkResponse.from_orm(homework).model_dump())


@router.delete("/{uuid}")
def delete_homework(
    *,
    db: Session = Depends(deps.get_mysql_db),
    uuid: str,
):
    """
    Delete a homework.
    """
    homework = crud_homework.get_homework_by_uuid(db=db, uuid=uuid)
    if not homework:
        return NotFound(message="Homework not found")
    homework = crud_homework.remove_homework(db=db, db_obj=homework)
    return Success(data=HomeworkResponse.from_orm(homework).model_dump())
