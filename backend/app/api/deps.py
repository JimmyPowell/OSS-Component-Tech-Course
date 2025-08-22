from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError

from app import crud, models
from app.config.mysql_config import get_mysql_db as get_db
from app.utils import security
from app.crud import crud_user

bearer_scheme = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = security.decode_token(token)
    if payload is None:
        raise credentials_exception
    
    user_uuid = payload.get("sub")
    role = payload.get("role")
    if user_uuid is None or role is None:
        raise credentials_exception
        
    return {
        "uuid": user_uuid,
        "role": role
    }

def get_current_active_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Dependency to ensure current user is active (JWT-based, no DB query)"""
    # For JWT-based auth, we assume active users only get valid tokens
    return current_user

def get_current_manager_user(
    current_user: dict = Depends(get_current_active_user)
) -> dict:
    """Dependency to ensure current user is a manager"""
    if current_user.get("role") != "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Manager role required."
        )
    return current_user

def get_current_user_obj(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> models.User:
    """Dependency to get current user as User object from database"""
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = security.decode_token(token)
    if payload is None:
        raise credentials_exception
    
    user_uuid = payload.get("sub")
    if user_uuid is None:
        raise credentials_exception
    
    user = crud_user.get_user_by_uuid(db, uuid=user_uuid)
    if user is None:
        raise credentials_exception
    
    return user

def get_current_manager_user_obj(
    current_user: models.User = Depends(get_current_user_obj)
) -> models.User:
    """Dependency to ensure current user is a manager (returns User object)"""
    if current_user.role != "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Manager role required."
        )
    return current_user
