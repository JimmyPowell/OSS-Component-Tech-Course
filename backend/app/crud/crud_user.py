from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.models.user import User
from app.schemas.user import UserUpdate, UserSearchRequest
from app.utils.security import hash_password
from typing import Tuple, List, Optional
import uuid

def get_user_by_uuid(db: Session, uuid: str) -> User:
    return db.query(User).filter(User.uuid == uuid).first()

def get_user_by_email(db: Session, email: str) -> User:
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> User:
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user_data: dict) -> User:
    hashed_password = hash_password(user_data["password"])
    db_user = User(
        uuid=str(uuid.uuid4()),
        username=user_data["username"],
        email=user_data["email"],
        hashed_password=hashed_password,
        real_name=user_data["real_name"],
        phone_number=user_data["phone_number"],
        school=user_data["school"],
        avatar_url=user_data.get("avatar_url"),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def admin_create_user(db: Session, user_data: dict) -> User:
    """Admin directly creates user without registration flow"""
    hashed_password = hash_password(user_data["password"])
    db_user = User(
        uuid=str(uuid.uuid4()),
        username=user_data["username"],
        email=user_data["email"],
        hashed_password=hashed_password,
        real_name=user_data["real_name"],
        phone_number=user_data["phone_number"],
        school=user_data.get("school"),
        role=user_data.get("role", "user"),
        avatar_url=user_data.get("avatar_url"),
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_password(db: Session, user_id: int, new_password: str):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.hashed_password = hash_password(new_password)
        db.commit()
        db.refresh(user)
    return user

# Admin user management functions
def get_users_with_pagination(
    db: Session, 
    skip: int = 0, 
    limit: int = 20,
    search_params: Optional[UserSearchRequest] = None
) -> Tuple[int, List[User]]:
    """Get users with pagination and optional search/filter"""
    query = db.query(User).filter(User.deleted_at.is_(None))
    
    if search_params:
        if search_params.search:
            search_term = f"%{search_params.search}%"
            query = query.filter(
                or_(
                    User.username.like(search_term),
                    User.email.like(search_term),
                    User.uuid.like(search_term),
                    User.real_name.like(search_term)
                )
            )
        
        if search_params.role:
            query = query.filter(User.role == search_params.role)
            
        if search_params.is_active is not None:
            query = query.filter(User.is_active == search_params.is_active)
            
        if search_params.school:
            query = query.filter(User.school.like(f"%{search_params.school}%"))
    
    total = query.count()
    users = query.offset(skip).limit(limit).all()
    
    return total, users

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(
        and_(User.id == user_id, User.deleted_at.is_(None))
    ).first()

def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    """Update user information"""
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user

def ban_user(db: Session, user_id: int) -> Optional[User]:
    """Ban user (set is_active to False)"""
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user

def unban_user(db: Session, user_id: int) -> Optional[User]:
    """Unban user (set is_active to True)"""
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    
    user.is_active = True
    db.commit()
    db.refresh(user)
    return user

def soft_delete_user(db: Session, user_id: int) -> Optional[User]:
    """Soft delete user (set deleted_at timestamp)"""
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    
    from datetime import datetime
    user.deleted_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return user
