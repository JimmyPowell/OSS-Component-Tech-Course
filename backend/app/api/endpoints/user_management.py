from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app import models, crud
from app.schemas.user import UserUpdate, UserSearchRequest, UserResponse, AdminUserCreate, AdminPasswordResetRequest
from app.api import deps
from app.utils.response import Success, BadRequest, NotFound, Created

router = APIRouter()

@router.post("/")
def create_user(
    user_data: AdminUserCreate,
    db: Session = Depends(deps.get_db),
    current_manager: models.User = Depends(deps.get_current_manager_user_obj)
):
    """
    Create user directly by admin (Manager only).
    """
    # Check if username already exists
    if crud.crud_user.get_user_by_username(db=db, username=user_data.username):
        return BadRequest(message="Username already exists")
    
    # Check if email already exists
    if crud.crud_user.get_user_by_email(db=db, email=str(user_data.email)):
        return BadRequest(message="Email already exists")
    
    # Create user
    user = crud.crud_user.admin_create_user(db=db, user_data=user_data.dict())
    
    return Created(
        data=UserResponse.from_orm(user).dict(),
        message="User created successfully"
    )

@router.get("/")
def get_users(
    skip: int = Query(0, ge=0, description="Skip records"),
    limit: int = Query(20, ge=1, le=100, description="Limit records"),
    search: Optional[str] = Query(None, description="Search by username, email, uuid, or real name"),
    role: Optional[str] = Query(None, description="Filter by role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    school: Optional[str] = Query(None, description="Filter by school"),
    db: Session = Depends(deps.get_db),
    current_manager: models.User = Depends(deps.get_current_manager_user_obj)
):
    """
    Get users with pagination and optional search/filter (Manager only).
    """
    search_params = UserSearchRequest(
        search=search,
        role=role,
        is_active=is_active,
        school=school
    )
    
    total, users = crud.crud_user.get_users_with_pagination(
        db=db, 
        skip=skip, 
        limit=limit, 
        search_params=search_params
    )
    
    user_responses = [UserResponse.from_orm(user).dict() for user in users]
    
    return Success(data={
        "total": total,
        "items": user_responses,
        "page": skip // limit + 1,
        "limit": limit
    })

@router.get("/{user_id}")
def get_user(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_manager: models.User = Depends(deps.get_current_manager_user_obj)
):
    """
    Get user by ID (Manager only).
    """
    user = crud.crud_user.get_user_by_id(db=db, user_id=user_id)
    if not user:
        return NotFound(message="User not found")
    
    return Success(data=UserResponse.from_orm(user).dict())

@router.put("/{user_id}")
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(deps.get_db),
    current_manager: models.User = Depends(deps.get_current_manager_user_obj)
):
    """
    Update user information (Manager only).
    """
    # Check if user exists
    existing_user = crud.crud_user.get_user_by_id(db=db, user_id=user_id)
    if not existing_user:
        return NotFound(message="User not found")
    
    # Check for username/email conflicts if they're being updated
    if user_update.username and user_update.username != existing_user.username:
        if crud.crud_user.get_user_by_username(db=db, username=user_update.username):
            return BadRequest(message="Username already exists")
    
    if user_update.email and user_update.email != existing_user.email:
        if crud.crud_user.get_user_by_email(db=db, email=str(user_update.email)):
            return BadRequest(message="Email already exists")
    
    updated_user = crud.crud_user.update_user(db=db, user_id=user_id, user_update=user_update)
    if not updated_user:
        return BadRequest(message="Failed to update user")
    
    return Success(data=UserResponse.from_orm(updated_user).dict())

@router.post("/{user_id}/ban")
def ban_user(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_manager: models.User = Depends(deps.get_current_manager_user_obj)
):
    """
    Ban user (set is_active to False) (Manager only).
    """
    print(f"API: 尝试封禁用户 {user_id}，管理员: {current_manager.id}")
    
    # Prevent managers from banning themselves
    if user_id == current_manager.id:
        print(f"API: 管理员不能封禁自己")
        return BadRequest(message="Cannot ban yourself")
    
    user = crud.crud_user.ban_user(db=db, user_id=user_id)
    if not user:
        print(f"API: 用户 {user_id} 未找到")
        return NotFound(message="User not found")
    
    print(f"API: 用户 {user_id} 封禁成功，状态: {user.is_active}")
    return Success(
        data=UserResponse.from_orm(user).dict(),
        message="User banned successfully"
    )

@router.post("/{user_id}/unban")
def unban_user(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_manager: models.User = Depends(deps.get_current_manager_user_obj)
):
    """
    Unban user (set is_active to True) (Manager only).
    """
    print(f"API: 尝试解封用户 {user_id}，管理员: {current_manager.id}")
    
    user = crud.crud_user.unban_user(db=db, user_id=user_id)
    if not user:
        print(f"API: 用户 {user_id} 未找到")
        return NotFound(message="User not found")
    
    print(f"API: 用户 {user_id} 解封成功，状态: {user.is_active}")
    return Success(
        data=UserResponse.from_orm(user).dict(),
        message="User unbanned successfully"
    )

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_manager: models.User = Depends(deps.get_current_manager_user_obj)
):
    """
    Soft delete user (Manager only).
    """
    # Prevent managers from deleting themselves
    if user_id == current_manager.id:
        return BadRequest(message="Cannot delete yourself")
    
    user = crud.crud_user.soft_delete_user(db=db, user_id=user_id)
    if not user:
        return NotFound(message="User not found")
    
    return Success(
        data=UserResponse.from_orm(user).dict(),
        message="User deleted successfully"
    )

@router.post("/{user_id}/reset-password")
def reset_user_password(
    user_id: int,
    password_data: AdminPasswordResetRequest,
    db: Session = Depends(deps.get_db),
    current_manager: models.User = Depends(deps.get_current_manager_user_obj)
):
    """
    Reset user password by admin (Manager only).
    """
    # Prevent managers from resetting their own password
    if user_id == current_manager.id:
        return BadRequest(message="Cannot reset your own password. Please use change password feature instead.")
    
    # Check if user exists
    user = crud.crud_user.get_user_by_id(db=db, user_id=user_id)
    if not user:
        return NotFound(message="User not found")
    
    # Update user password
    updated_user = crud.crud_user.update_user_password(db=db, user_id=user_id, new_password=password_data.new_password)
    if not updated_user:
        return BadRequest(message="Failed to reset password")
    
    # Log the operation (optional: you can add logging here)
    # logger.info(f"Manager {current_manager.username} reset password for user {user.username}")
    
    return Success(
        data=UserResponse.from_orm(updated_user).dict(),
        message="Password reset successfully"
    )