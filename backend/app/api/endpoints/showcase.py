from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.api import deps
from app.crud import crud_showcase
from app.models import User
from app.schemas.showcase import (
    ShowcaseCreate,
    ShowcaseUpdate,
    ShowcaseResponse,
    ShowcaseReviewRequest,
)
from app.utils.response import Success, NotFound, BadRequest

router = APIRouter()

# 管理员路由
admin_router = APIRouter()


# 管理员创建作品端点
@admin_router.post("/")
def create_showcase_admin(
    *,
    db: Session = Depends(deps.get_db),
    showcase_in: ShowcaseCreate,
    current_user: User = Depends(deps.get_current_manager_user_obj),
):
    """
    Create new showcase (Admin only).
    """
    existing_showcase = crud_showcase.get_by_name(db=db, name=showcase_in.name)
    if existing_showcase:
        return BadRequest(message="Showcase with this name already exists.")
        
    showcase = crud_showcase.create_showcase(db=db, showcase_in=showcase_in, author_id=current_user.id)
    return Success(data=ShowcaseResponse.from_orm(showcase).model_dump())

@router.post("/")
def create_showcase(
    *,
    db: Session = Depends(deps.get_db),
    showcase_in: ShowcaseCreate,
    current_user: User = Depends(deps.get_current_user_obj),
):
    """
    Create new showcase.
    """
    existing_showcase = crud_showcase.get_by_name(db=db, name=showcase_in.name)
    if existing_showcase:
        return BadRequest(message="Showcase with this name already exists.")
        
    showcase = crud_showcase.create_showcase(db=db, showcase_in=showcase_in, author_id=current_user.id)
    return Success(data=ShowcaseResponse.from_orm(showcase).model_dump())


# 管理员查看作品端点
@admin_router.get("/")
def read_showcases_admin(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_manager_user_obj),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    name: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
):
    """
    Retrieve showcases with pagination and filtering (Admin only).
    """
    total, showcases = crud_showcase.get_multi(
        db,
        skip=skip,
        limit=limit,
        name=name,
        status=status,
        start_time=start_time,
        end_time=end_time,
    )
    return Success(data={"total": total, "items": [ShowcaseResponse.from_orm(s).model_dump() for s in showcases]})

@router.get("/")
def read_showcases(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    name: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
):
    """
    Retrieve showcases with pagination and filtering.
    """
    total, showcases = crud_showcase.get_multi(
        db,
        skip=skip,
        limit=limit,
        name=name,
        status=status,
        start_time=start_time,
        end_time=end_time,
    )
    return Success(data={"total": total, "items": [ShowcaseResponse.from_orm(s).model_dump() for s in showcases]})


# 管理员获取待审核作品列表
@admin_router.get("/pending-review")
def get_pending_review_showcases_admin(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_manager_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """
    Get showcases pending review (Admin only).
    """
    print(f"获取待审核作品列表 - 用户: {current_user.id}, skip: {skip}, limit: {limit}")
    total, showcases = crud_showcase.get_multi(
        db,
        skip=skip,
        limit=limit,
        status="pending_review",
    )
    print(f"查询结果 - total: {total}, showcases count: {len(showcases)}")
    result = {"total": total, "items": [ShowcaseResponse.from_orm(s).model_dump() for s in showcases]}
    print(f"返回数据: {result}")
    return Success(data=result)


# 管理员查看单个作品端点
@admin_router.get("/{uuid}")
def read_showcase_admin(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
    current_user: User = Depends(deps.get_current_manager_user),
):
    """
    Get showcase by UUID (Admin only).
    """
    showcase = crud_showcase.get_showcase_by_uuid(db=db, uuid=uuid)
    if not showcase:
        return NotFound(message="Showcase not found")
    return Success(data=ShowcaseResponse.from_orm(showcase).model_dump())

@router.get("/{uuid}")
def read_showcase(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
):
    """
    Get showcase by UUID.
    """
    showcase = crud_showcase.get_showcase_by_uuid(db=db, uuid=uuid)
    if not showcase:
        return NotFound(message="Showcase not found")
    return Success(data=ShowcaseResponse.from_orm(showcase).model_dump())


# 管理员更新作品端点
@admin_router.put("/{uuid}")
def update_showcase_admin(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
    showcase_in: ShowcaseUpdate,
    current_user: User = Depends(deps.get_current_manager_user),
):
    """
    Update a showcase (Admin only).
    """
    showcase = crud_showcase.get_showcase_by_uuid(db=db, uuid=uuid)
    if not showcase:
        return NotFound(message="Showcase not found")
    showcase = crud_showcase.update_showcase(db=db, db_obj=showcase, obj_in=showcase_in)
    return Success(data=ShowcaseResponse.from_orm(showcase).model_dump())

@router.put("/{uuid}")
def update_showcase(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
    showcase_in: ShowcaseUpdate,
    current_user: User = Depends(deps.get_current_user_obj),
):
    """
    Update a showcase. Users can only update their own showcases.
    """
    showcase = crud_showcase.get_showcase_by_uuid(db=db, uuid=uuid)
    if not showcase:
        return NotFound(message="Showcase not found")
    
    # Check if user is the author of the showcase
    if showcase.author_id != current_user.id:
        return BadRequest(message="You can only update your own showcases")
    
    showcase = crud_showcase.update_showcase(db=db, db_obj=showcase, obj_in=showcase_in)
    return Success(data=ShowcaseResponse.from_orm(showcase).model_dump())


# 管理员删除作品端点
@admin_router.delete("/{uuid}")
def delete_showcase_admin(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
    current_user: User = Depends(deps.get_current_manager_user),
):
    """
    Delete a showcase (Admin only).
    """
    showcase = crud_showcase.get_showcase_by_uuid(db=db, uuid=uuid)
    if not showcase:
        return NotFound(message="Showcase not found")
    showcase = crud_showcase.remove_showcase(db=db, db_obj=showcase)
    return Success(data=ShowcaseResponse.from_orm(showcase).model_dump())

@router.delete("/{uuid}")
def delete_showcase(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
    current_user: User = Depends(deps.get_current_user_obj),
):
    """
    Delete a showcase. Users can only delete their own showcases.
    """
    showcase = crud_showcase.get_showcase_by_uuid(db=db, uuid=uuid)
    if not showcase:
        return NotFound(message="Showcase not found")
    
    # Check if user is the author of the showcase
    if showcase.author_id != current_user.id:
        return BadRequest(message="You can only delete your own showcases")
    
    showcase = crud_showcase.remove_showcase(db=db, db_obj=showcase)
    return Success(data=ShowcaseResponse.from_orm(showcase).model_dump())


# 管理员审核作品端点
@admin_router.post("/{uuid}/review")
def review_showcase_admin(
    *,
    db: Session = Depends(deps.get_db),
    uuid: str,
    review_request: ShowcaseReviewRequest,
    current_user: User = Depends(deps.get_current_manager_user),
):
    """
    Review a showcase (approve/reject) - Admin only.
    """
    showcase = crud_showcase.get_showcase_by_uuid(db=db, uuid=uuid)
    if not showcase:
        return NotFound(message="Showcase not found")
    
    if showcase.status not in ['pending_review', 'draft']:
        return BadRequest(message="Showcase cannot be reviewed in current status")
    
    if review_request.action == "approve":
        showcase = crud_showcase.approve_showcase(
            db=db, 
            db_obj=showcase, 
            reviewer_id=current_user.id,
            review_comment=review_request.review_comment
        )
    elif review_request.action == "reject":
        if not review_request.review_comment or not review_request.review_comment.strip():
            return BadRequest(message="Review comment is required when rejecting a showcase")
        showcase = crud_showcase.reject_showcase(
            db=db, 
            db_obj=showcase, 
            reviewer_id=current_user.id,
            review_comment=review_request.review_comment
        )
    
    return Success(data=ShowcaseResponse.from_orm(showcase).model_dump())
