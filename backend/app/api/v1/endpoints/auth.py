from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.user import User as UserModel, PlanType
from app.schemas.user import User, UserCreate

router = APIRouter()

@router.post("/webhook/clerk")
async def clerk_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Clerk webhooks for user events."""
    payload = await request.json()
    event_type = payload.get("type")
    
    if event_type == "user.created":
        user_data = payload.get("data", {})
        user_id = user_data.get("id")
        email = user_data.get("email_addresses", [{}])[0].get("email_address")
        name = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
        
        # Check if user already exists
        existing = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not existing:
            user = UserModel(
                id=user_id,
                email=email,
                name=name or None,
                plan=PlanType.FREE
            )
            db.add(user)
            db.commit()
        
        return {"status": "success"}
    
    elif event_type == "user.updated":
        user_data = payload.get("data", {})
        user_id = user_data.get("id")
        
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if user:
            email = user_data.get("email_addresses", [{}])[0].get("email_address")
            name = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
            
            user.email = email
            user.name = name or user.name
            db.commit()
        
        return {"status": "success"}
    
    elif event_type == "user.deleted":
        user_id = payload.get("data", {}).get("id")
        
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if user:
            db.delete(user)
            db.commit()
        
        return {"status": "success"}
    
    return {"status": "ignored"}

@router.get("/me", response_model=User)
async def get_current_user(
    user_id: str = "user-1",
    db: Session = Depends(get_db)
):
    """Get current user profile."""
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
