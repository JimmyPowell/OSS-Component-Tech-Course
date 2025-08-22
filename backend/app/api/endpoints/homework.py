from fastapi import APIRouter, Depends, HTTPException, Query
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
    HomeworkDetailResponse,
)
from app.utils.response import Success, NotFound, BadRequest

router = APIRouter()

# 管理员路由
admin_router = APIRouter()


# 管理员创建作业端点
@admin_router.post("/")
def create_homework_admin(
    *,
    db: Session = Depends(deps.get_db),
    homework_in: HomeworkCreate,
    current_user: User = Depends(deps.get_current_manager_user),
):
    """
    Create new homework (Admin only).
    """
    existing_homework = crud_homework.get_by_name(db=db, name=homework_in.name)
    if existing_homework:
        return BadRequest(message="Homework with this name already exists.")
        
    homework = crud_homework.create_homework(db=db, homework_in=homework_in, creator_id=current_user.id)
    return Success(data=HomeworkResponse.from_orm(homework).model_dump())

@router.post("/")
def create_homework(
    *,
    db: Session = Depends(deps.get_db),
    homework_in: HomeworkCreate,
    current_user: dict = Depends(deps.get_current_manager_user),
):
    """
    Create new homework. Requires manager role.
    """
    existing_homework = crud_homework.get_by_name(db=db, name=homework_in.name)
    if existing_homework:
        return BadRequest(message="Homework with this name already exists.")
    
    # Get user ID from database using UUID (only for create operations where we need the ID)
    from app.crud import crud_user
    user = crud_user.get_user_by_uuid(db=db, uuid=current_user["uuid"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    homework = crud_homework.create_homework(db=db, homework_in=homework_in, creator_id=user.id)
    return Success(data=HomeworkResponse.from_orm(homework).model_dump())


# 管理员查看作业端点
@admin_router.get("/")
def read_homeworks_admin(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_manager_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    name: Optional[str] = Query(None),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
):
    """
    Retrieve homeworks with pagination and filtering (Admin only).
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

@router.get("/")
def read_homeworks(
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    name: Optional[str] = Query(None),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
):
    """
    Retrieve homeworks with pagination and filtering.
    Requires authentication.
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


# 管理员查看单个作业端点
@admin_router.get("/{uuid}")
def read_homework_admin(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
    current_user: User = Depends(deps.get_current_manager_user),
):
    """
    Get homework by UUID (Admin only).
    """
    homework = crud_homework.get_homework_by_uuid(db=db, uuid=uuid)
    if not homework:
        return NotFound(message="Homework not found")
    return Success(data=HomeworkResponse.from_orm(homework).model_dump())

@router.get("/{uuid}")
def read_homework(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
    current_user: dict = Depends(deps.get_current_user),
):
    """
    Get homework by UUID with publisher information.
    Requires authentication.
    """
    homework_detail = crud_homework.get_homework_detail_by_uuid(db=db, uuid=uuid)
    if not homework_detail:
        return NotFound(message="Homework not found")
    return Success(data=homework_detail)


# 管理员更新作业端点
@admin_router.put("/{uuid}")
def update_homework_admin(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
    homework_in: HomeworkUpdate,
    current_user: User = Depends(deps.get_current_manager_user),
):
    """
    Update a homework (Admin only).
    """
    homework = crud_homework.get_homework_by_uuid(db=db, uuid=uuid)
    if not homework:
        return NotFound(message="Homework not found")
    homework = crud_homework.update_homework(db=db, db_obj=homework, obj_in=homework_in)
    return Success(data=HomeworkResponse.from_orm(homework).model_dump())

@router.put("/{uuid}")
def update_homework(
    *,
    db: Session = Depends(deps.get_db),
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


# 管理员删除作业端点
@admin_router.delete("/{uuid}")
def delete_homework_admin(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
    current_user: User = Depends(deps.get_current_manager_user),
):
    """
    Delete a homework (Admin only).
    """
    homework = crud_homework.get_homework_by_uuid(db=db, uuid=uuid)
    if not homework:
        return NotFound(message="Homework not found")
    homework = crud_homework.remove_homework(db=db, db_obj=homework)
    return Success(data=HomeworkResponse.from_orm(homework).model_dump())

@router.delete("/{uuid}")
def delete_homework(
    *,
    db: Session = Depends(deps.get_db),
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
