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
        student_id=user_data.get("student_id"),
        student_class=user_data.get("student_class"),
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
    
    print(f"封禁用户前: user_id={user_id}, is_active={user.is_active}")
    user.is_active = False
    db.add(user)  # 显式添加到会话
    db.commit()
    db.refresh(user)
    print(f"封禁用户后: user_id={user_id}, is_active={user.is_active}")
    return user

def unban_user(db: Session, user_id: int) -> Optional[User]:
    """Unban user (set is_active to True)"""
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    
    print(f"解封用户前: user_id={user_id}, is_active={user.is_active}")
    user.is_active = True
    db.add(user)  # 显式添加到会话
    db.commit()
    db.refresh(user)
    print(f"解封用户后: user_id={user_id}, is_active={user.is_active}")
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

def get_user_by_student_id(db: Session, student_id: str) -> Optional[User]:
    """Get user by student ID"""
    return db.query(User).filter(
        and_(User.student_id == student_id, User.deleted_at.is_(None))
    ).first()

def check_batch_import_conflicts(db: Session, users_data: List[dict]) -> List[dict]:
    """Check for conflicts in batch import data"""
    conflicts = []
    
    for index, user_data in enumerate(users_data):
        student_id = user_data.get("student_id")
        real_name = user_data.get("real_name")
        username = real_name  # Username is same as real_name in batch import
        
        # Check for student_id conflict
        if student_id and get_user_by_student_id(db, student_id):
            existing_user = get_user_by_student_id(db, student_id)
            conflicts.append({
                "row_index": index,
                "student_id": student_id,
                "real_name": real_name,
                "student_class": user_data.get("student_class", ""),
                "conflict_type": "student_id",
                "existing_user": {
                    "username": existing_user.username,
                    "real_name": existing_user.real_name,
                    "avatar_url": existing_user.avatar_url
                }
            })
            continue
            
        # Check for real_name conflict (as username)
        if real_name and get_user_by_username(db, real_name):
            existing_user = get_user_by_username(db, real_name)
            conflicts.append({
                "row_index": index,
                "student_id": student_id,
                "real_name": real_name,
                "student_class": user_data.get("student_class", ""),
                "conflict_type": "username",
                "existing_user": {
                    "username": existing_user.username,
                    "real_name": existing_user.real_name,
                    "avatar_url": existing_user.avatar_url
                }
            })
    
    return conflicts

def batch_create_users(db: Session, users_data: List[dict], conflict_resolution: str = "cancel") -> dict:
    """Batch create users with conflict resolution"""
    created_users = []
    errors = []
    
    try:
        for index, user_data in enumerate(users_data):
            try:
                # Handle conflicts based on resolution strategy
                if conflict_resolution == "overwrite":
                    # Delete existing user if exists
                    existing_user = None
                    if user_data.get("student_id"):
                        existing_user = get_user_by_student_id(db, user_data["student_id"])
                    if not existing_user and user_data.get("real_name"):
                        existing_user = get_user_by_username(db, user_data["real_name"])
                    
                    if existing_user:
                        db.delete(existing_user)
                        db.flush()
                
                # Create new user
                username = user_data["real_name"]
                password = user_data["real_name"]  # Password same as real_name
                # Generate temporary email with valid domain
                import time
                email = f"{username}_{int(time.time())}@example.com"
                
                new_user_data = {
                    "username": username,
                    "email": email,
                    "password": password,
                    "real_name": user_data["real_name"],
                    "phone_number": "",
                    "school": "",
                    "student_id": user_data.get("student_id"),
                    "student_class": user_data.get("student_class"),
                    "role": "user"
                }
                
                user = admin_create_user(db, new_user_data)
                created_users.append(user)
                
            except Exception as e:
                errors.append(f"Row {index + 1}: {str(e)}")
                continue
        
        db.commit()
        
        return {
            "success_count": len(created_users),
            "error_count": len(errors),
            "errors": errors,
            "created_users": created_users
        }
        
    except Exception as e:
        db.rollback()
        raise e
