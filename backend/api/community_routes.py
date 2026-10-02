"""Board posts require staff moderation; moderation is not agronomic verification."""
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import or_
from apps.community.models import CommunityPost
from apps.farmer_profile.models import User
from core.database import get_db
from core.security import get_current_user, require_officer

router = APIRouter(prefix='/api/community', tags=['community'])


class PostInput(BaseModel):
    board: Literal['Paddy', 'Banana', 'Coconut', 'Pepper', 'Machinery', 'Market', 'Schemes']
    title: str = Field(min_length=5, max_length=120)
    body: str = Field(min_length=20, max_length=3000)


class ModerationInput(BaseModel):
    status: Literal['Published', 'Not published']


@router.get('')
def posts(db=Depends(get_db), user=Depends(get_current_user)):
    query = db.query(CommunityPost)
    if user.role == 'FARMER':
        query = query.filter(or_(CommunityPost.status == 'Published', CommunityPost.author_id == user.id))
    return [{"id": p.id, "title": p.title, "body": p.body, "board": p.board, "status": p.status,
             "label": p.label, "author": db.get(User,p.author_id).full_name.split(' (')[0], "created_at":p.created_at}
            for p in query.order_by(CommunityPost.id.desc()).all()]


@router.post('', status_code=201)
def create(payload: PostInput, db=Depends(get_db), user=Depends(get_current_user)):
    row = CommunityPost(**payload.model_dump(),author_id=user.id,
                        label='Expert notice' if user.role in ('OFFICER','ADMIN') else 'Farmer experience')
    db.add(row)
    db.commit()
    return {"id": row.id, "status": row.status}


@router.patch('/{post_id}')
def moderate(post_id: int, payload: ModerationInput, db=Depends(get_db), user=Depends(require_officer)):
    row = db.get(CommunityPost,post_id)
    if not row:
        raise HTTPException(404,'Post not found')
    row.status = payload.status
    row.reviewed_by = user.id
    db.commit()
    return {"status": row.status}
