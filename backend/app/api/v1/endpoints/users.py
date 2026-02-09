from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.user import User as UserModel
from app.schemas.user import User, UserUpdate

router = APIRouter()

@router.get("/me", response_model=User)
async def get_me(
    user_id: str = "user-1",
    db: Session = Depends(get_db)
):
    """Get current user."""
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/me", response_model=User)
async def update_me(
    user_update: UserUpdate,
    user_id: str = "user-1",
    db: Session = Depends(get_db)
):
    """Update current user profile."""
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user
