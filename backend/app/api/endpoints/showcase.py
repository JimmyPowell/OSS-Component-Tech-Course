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
)
from app.utils.response import Success, NotFound, BadRequest

router = APIRouter()


@router.post("/")
def create_showcase(
    *,
    db: Session = Depends(deps.get_mysql_db),
    showcase_in: ShowcaseCreate,
    current_user: User = Depends(deps.get_current_user),
):
    """
    Create new showcase.
    """
    existing_showcase = crud_showcase.get_by_name(db=db, name=showcase_in.name)
    if existing_showcase:
        return BadRequest(message="Showcase with this name already exists.")
        
    showcase = crud_showcase.create_showcase(db=db, showcase_in=showcase_in, author_id=current_user.id)
    return Success(data=ShowcaseResponse.from_orm(showcase).model_dump())


@router.get("/")
def read_showcases(
    db: Session = Depends(deps.get_mysql_db),
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


@router.get("/{uuid}")
def read_showcase(
    *,
    db: Session = Depends(deps.get_mysql_db),
    uuid: str,
):
    """
    Get showcase by UUID.
    """
    showcase = crud_showcase.get_showcase_by_uuid(db=db, uuid=uuid)
    if not showcase:
        return NotFound(message="Showcase not found")
    return Success(data=ShowcaseResponse.from_orm(showcase).model_dump())


@router.put("/{uuid}")
def update_showcase(
    *,
    db: Session = Depends(deps.get_mysql_db),
    uuid: str,
    showcase_in: ShowcaseUpdate,
):
    """
    Update a showcase.
    """
    showcase = crud_showcase.get_showcase_by_uuid(db=db, uuid=uuid)
    if not showcase:
        return NotFound(message="Showcase not found")
    showcase = crud_showcase.update_showcase(db=db, db_obj=showcase, obj_in=showcase_in)
    return Success(data=ShowcaseResponse.from_orm(showcase).model_dump())


@router.delete("/{uuid}")
def delete_showcase(
    *,
    db: Session = Depends(deps.get_mysql_db),
    uuid: str,
):
    """
    Delete a showcase.
    """
    showcase = crud_showcase.get_showcase_by_uuid(db=db, uuid=uuid)
    if not showcase:
        return NotFound(message="Showcase not found")
    showcase = crud_showcase.remove_showcase(db=db, db_obj=showcase)
    return Success(data=ShowcaseResponse.from_orm(showcase).model_dump())
