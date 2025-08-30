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
    HomeworkStatusUpdate,
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
    current_user: User = Depends(deps.get_current_manager_user_obj),
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
    current_user: User = Depends(deps.get_current_manager_user_obj),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    name: Optional[str] = Query(None),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    status: Optional[str] = Query(None, description="作业状态过滤：draft, published"),
):
    """
    Retrieve homeworks with pagination and filtering (Admin only).
    管理员可以查看所有状态的作业，也可以按状态过滤。
    """
    total, homeworks = crud_homework.get_multi(
        db,
        skip=skip,
        limit=limit,
        name=name,
        start_time=start_time,
        end_time=end_time,
        status=status,
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
    Retrieve published homeworks with pagination and filtering.
    普通用户只能查看已发布的作业。
    """
    total, homeworks = crud_homework.get_multi(
        db,
        skip=skip,
        limit=limit,
        name=name,
        start_time=start_time,
        end_time=end_time,
        status="published"  # 普通用户只能查看已发布的作业
    )
    return Success(data={"total": total, "items": [HomeworkResponse.from_orm(h).model_dump() for h in homeworks]})


# 管理员查看单个作业端点
@admin_router.get("/{uuid}")
def read_homework_admin(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
    current_user: User = Depends(deps.get_current_manager_user_obj),
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
    Get published homework by UUID with publisher information.
    普通用户只能查看已发布的作业。
    """
    homework_detail = crud_homework.get_homework_detail_by_uuid(
        db=db, 
        uuid=uuid,
        status_filter="published"  # 普通用户只能查看已发布的作业
    )
    if not homework_detail:
        return NotFound(message="Homework not found or not published")
    return Success(data=homework_detail)


# 管理员更新作业端点
@admin_router.put("/{uuid}")
def update_homework_admin(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
    homework_in: HomeworkUpdate,
    current_user: User = Depends(deps.get_current_manager_user_obj),
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
    current_user: User = Depends(deps.get_current_manager_user_obj),
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


# 状态切换接口
@router.put("/{uuid}/status")
def update_homework_status(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
    status_update: HomeworkStatusUpdate,
    current_user: dict = Depends(deps.get_current_manager_user),
):
    """
    Update homework status (Manager only).
    """
    homework = crud_homework.get_homework_by_uuid(db=db, uuid=uuid)
    if not homework:
        return NotFound(message="Homework not found")
    
    # 更新状态
    homework.status = status_update.status.value
    db.commit()
    db.refresh(homework)
    
    status_text = "已发布" if status_update.status.value == "published" else "未发布"
    return Success(
        data=HomeworkResponse.from_orm(homework).model_dump(),
        message=f"作业状态已更新为：{status_text}"
    )


# 管理员状态切换接口
@admin_router.put("/{uuid}/status")
def update_homework_status_admin(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
    status_update: HomeworkStatusUpdate,
    current_user: User = Depends(deps.get_current_manager_user_obj),
):
    """
    Update homework status (Admin only).
    """
    homework = crud_homework.get_homework_by_uuid(db=db, uuid=uuid)
    if not homework:
        return NotFound(message="Homework not found")
    
    # 更新状态
    homework.status = status_update.status.value
    db.commit()
    db.refresh(homework)
    
    status_text = "已发布" if status_update.status.value == "published" else "未发布"
    return Success(
        data=HomeworkResponse.from_orm(homework).model_dump(),
        message=f"作业状态已更新为：{status_text}"
    )
