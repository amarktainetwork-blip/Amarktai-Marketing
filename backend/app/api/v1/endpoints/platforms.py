from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.db.base import get_db
from app.models.platform_connection import PlatformConnection as PlatformModel, PlatformType
from app.schemas.platform import PlatformConnection, PlatformConnectionCreate

router = APIRouter()

@router.get("/", response_model=List[PlatformConnection])
async def get_platforms(
    user_id: str = "user-1",
    db: Session = Depends(get_db)
):
    """Get all connected platforms for the current user."""
    platforms = db.query(PlatformModel).filter(
        PlatformModel.user_id == user_id,
        PlatformModel.is_active == True
    ).all()
    return platforms

@router.get("/{platform}", response_model=PlatformConnection)
async def get_platform(
    platform: PlatformType,
    user_id: str = "user-1",
    db: Session = Depends(get_db)
):
    """Get a specific platform connection."""
    connection = db.query(PlatformModel).filter(
        PlatformModel.user_id == user_id,
        PlatformModel.platform == platform
    ).first()
    if not connection:
        raise HTTPException(status_code=404, detail="Platform not connected")
    return connection

@router.post("/{platform}/connect", response_model=PlatformConnection)
async def connect_platform(
    platform: PlatformType,
    account_name: str,
    user_id: str = "user-1",
    db: Session = Depends(get_db)
):
    """Connect a new platform."""
    # Check if already connected
    existing = db.query(PlatformModel).filter(
        PlatformModel.user_id == user_id,
        PlatformModel.platform == platform
    ).first()
    
    if existing:
        existing.is_active = True
        existing.account_name = account_name
        db.commit()
        db.refresh(existing)
        return existing
    
    # Create new connection
    connection = PlatformModel(
        id=str(uuid.uuid4()),
        user_id=user_id,
        platform=platform,
        account_name=account_name,
        account_id=f"{platform}_{uuid.uuid4().hex[:8]}",
        is_active=True
    )
    db.add(connection)
    db.commit()
    db.refresh(connection)
    return connection

@router.post("/{platform}/disconnect")
async def disconnect_platform(
    platform: PlatformType,
    user_id: str = "user-1",
    db: Session = Depends(get_db)
):
    """Disconnect a platform."""
    connection = db.query(PlatformModel).filter(
        PlatformModel.user_id == user_id,
        PlatformModel.platform == platform
    ).first()
    
    if not connection:
        raise HTTPException(status_code=404, detail="Platform not connected")
    
    connection.is_active = False
    db.commit()
    return {"message": f"Disconnected from {platform}"}
