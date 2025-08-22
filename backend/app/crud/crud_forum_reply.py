from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from typing import Optional, Tuple, List
from datetime import datetime
import uuid

from app.models.forum_reply import ForumReply
from app.schemas.forum_reply import ForumReplyCreate, ForumReplyUpdate


def create_forum_reply(db: Session, *, reply_in: ForumReplyCreate, user_id: int) -> ForumReply:
    # 计算楼层号
    floor_number = get_next_floor_number(db, post_id=reply_in.post_id)
    
    db_obj = ForumReply(
        **reply_in.dict(exclude={"uuid"}), 
        uuid=str(uuid.uuid4()), 
        user_id=user_id,
        floor_number=floor_number
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    
    # 更新帖子回复信息
    from app.crud.crud_forum_post import update_reply_info
    update_reply_info(db, post_id=db_obj.post_id, user_id=user_id, increment=True)
    
    return db_obj


def get_forum_reply_by_uuid(db: Session, *, uuid: str) -> Optional[ForumReply]:
    return db.query(ForumReply).filter(
        ForumReply.uuid == uuid, 
        ForumReply.is_deleted == False,
        ForumReply.deleted_at.is_(None)
    ).first()


def get_forum_reply_by_id(db: Session, *, reply_id: int) -> Optional[ForumReply]:
    return db.query(ForumReply).filter(
        ForumReply.id == reply_id, 
        ForumReply.is_deleted == False,
        ForumReply.deleted_at.is_(None)
    ).first()


def get_next_floor_number(db: Session, *, post_id: int) -> int:
    """获取下一个楼层号"""
    max_floor = db.query(func.max(ForumReply.floor_number)).filter(
        ForumReply.post_id == post_id,
        ForumReply.is_deleted == False,
        ForumReply.deleted_at.is_(None)
    ).scalar()
    
    return (max_floor or 0) + 1


def get_replies_by_post(
    db: Session,
    *,
    post_id: int,
    skip: int = 0,
    limit: int = 20,
    parent_id: Optional[int] = None
) -> Tuple[int, List[ForumReply]]:
    """获取帖子的回复列表"""
    query = db.query(ForumReply).filter(
        ForumReply.post_id == post_id,
        ForumReply.is_deleted == False,
        ForumReply.deleted_at.is_(None)
    )
    
    if parent_id is not None:
        query = query.filter(ForumReply.parent_id == parent_id)
    else:
        # 只获取顶级回复（没有父回复的）
        query = query.filter(ForumReply.parent_id.is_(None))
    
    total = query.count()
    items = query.order_by(ForumReply.floor_number.asc()).offset(skip).limit(limit).all()
    
    return total, items


def get_replies_tree(db: Session, *, post_id: int) -> List[ForumReply]:
    """获取帖子的回复树结构"""
    # 获取所有回复
    all_replies = db.query(ForumReply).filter(
        ForumReply.post_id == post_id,
        ForumReply.is_deleted == False,
        ForumReply.deleted_at.is_(None)
    ).order_by(ForumReply.floor_number.asc()).all()
    
    # 构建树结构
    reply_dict = {reply.id: reply for reply in all_replies}
    root_replies = []
    
    for reply in all_replies:
        if reply.parent_id is None:
            root_replies.append(reply)
        else:
            parent = reply_dict.get(reply.parent_id)
            if parent:
                if not hasattr(parent, 'children'):
                    parent.children = []
                parent.children.append(reply)
    
    return root_replies


def get_user_replies(
    db: Session,
    *,
    user_id: int,
    skip: int = 0,
    limit: int = 20
) -> Tuple[int, List[ForumReply]]:
    """获取用户的回复列表"""
    query = db.query(ForumReply).filter(
        ForumReply.user_id == user_id,
        ForumReply.is_deleted == False,
        ForumReply.deleted_at.is_(None)
    )
    
    total = query.count()
    items = query.order_by(desc(ForumReply.created_at)).offset(skip).limit(limit).all()
    
    return total, items


def update_forum_reply(db: Session, *, db_obj: ForumReply, obj_in: ForumReplyUpdate) -> ForumReply:
    update_data = obj_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def remove_forum_reply(db: Session, *, db_obj: ForumReply) -> ForumReply:
    """软删除回复"""
    db_obj.is_deleted = True
    db_obj.deleted_at = datetime.utcnow()
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    
    # 更新帖子回复信息
    from app.crud.crud_forum_post import update_reply_info
    update_reply_info(db, post_id=db_obj.post_id, user_id=db_obj.user_id, increment=False)
    
    return db_obj


def get_recent_replies(db: Session, *, limit: int = 10) -> List[ForumReply]:
    """获取最新回复"""
    return db.query(ForumReply).filter(
        ForumReply.is_deleted == False,
        ForumReply.deleted_at.is_(None)
    ).order_by(desc(ForumReply.created_at)).limit(limit).all()