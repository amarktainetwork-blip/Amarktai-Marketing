from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.db.base import get_db
from app.models.content import Content as ContentModel, ContentStatus
from app.schemas.content import Content, ContentCreate, ContentUpdate, ContentPerformance

router = APIRouter()

@router.get("/", response_model=List[Content])
async def get_content(
    status: ContentStatus = None,
    user_id: str = "user-1",
    db: Session = Depends(get_db)
):
    """Get all content for the current user."""
    query = db.query(ContentModel).filter(ContentModel.user_id == user_id)
    if status:
        query = query.filter(ContentModel.status == status)
    content = query.order_by(ContentModel.created_at.desc()).all()
    return content

@router.get("/pending", response_model=List[Content])
async def get_pending_content(
    user_id: str = "user-1",
    db: Session = Depends(get_db)
):
    """Get pending content for approval."""
    content = db.query(ContentModel).filter(
        ContentModel.user_id == user_id,
        ContentModel.status == ContentStatus.PENDING
    ).order_by(ContentModel.created_at.desc()).all()
    return content

@router.get("/{content_id}", response_model=Content)
async def get_content_item(
    content_id: str,
    user_id: str = "user-1",
    db: Session = Depends(get_db)
):
    """Get a specific content item."""
    content = db.query(ContentModel).filter(
        ContentModel.id == content_id,
        ContentModel.user_id == user_id
    ).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return content

@router.post("/{content_id}/approve", response_model=Content)
async def approve_content(
    content_id: str,
    user_id: str = "user-1",
    db: Session = Depends(get_db)
):
    """Approve content for posting."""
    content = db.query(ContentModel).filter(
        ContentModel.id == content_id,
        ContentModel.user_id == user_id
    ).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    content.status = ContentStatus.APPROVED
    db.commit()
    db.refresh(content)
    return content

@router.post("/{content_id}/reject", response_model=Content)
async def reject_content(
    content_id: str,
    user_id: str = "user-1",
    db: Session = Depends(get_db)
):
    """Reject content."""
    content = db.query(ContentModel).filter(
        ContentModel.id == content_id,
        ContentModel.user_id == user_id
    ).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    content.status = ContentStatus.REJECTED
    db.commit()
    db.refresh(content)
    return content

@router.post("/approve-all")
async def approve_all_content(
    content_ids: List[str],
    user_id: str = "user-1",
    db: Session = Depends(get_db)
):
    """Approve multiple content items."""
    db.query(ContentModel).filter(
        ContentModel.id.in_(content_ids),
        ContentModel.user_id == user_id
    ).update({"status": ContentStatus.APPROVED})
    db.commit()
    return {"message": f"Approved {len(content_ids)} items"}

@router.put("/{content_id}", response_model=Content)
async def update_content(
    content_id: str,
    content_update: ContentUpdate,
    user_id: str = "user-1",
    db: Session = Depends(get_db)
):
    """Update content (e.g., edit caption)."""
    content = db.query(ContentModel).filter(
        ContentModel.id == content_id,
        ContentModel.user_id == user_id
    ).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    update_data = content_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(content, field, value)
    
    db.commit()
    db.refresh(content)
    return content
