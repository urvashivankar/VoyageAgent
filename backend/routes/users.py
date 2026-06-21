from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import User
from database.schemas import UserOut, UserProfileUpdate, UserSettingsUpdate
from typing import Dict, Any

# Mock dependency for getting current user (since auth.py might not fully be implemented with Depends for me here)
def get_current_user_mock(db: Session = Depends(get_db)):
    # For demo, just return the first user or create one
    user = db.query(User).first()
    if not user:
        user = User(name="Demo User", email="demo@trippilot.ai", mobile="0000000000")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/profile", response_model=UserOut)
def get_profile(current_user: User = Depends(get_current_user_mock)):
    """Get current user's profile and stats."""
    return current_user

@router.put("/profile", response_model=UserOut)
def update_profile(
    profile_data: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_mock)
):
    """Update user profile information."""
    if profile_data.name is not None:
        current_user.name = profile_data.name
    if profile_data.profile_picture is not None:
        current_user.profile_picture = profile_data.profile_picture
    if profile_data.travel_style is not None:
        current_user.travel_style = profile_data.travel_style
    if profile_data.preferred_currency is not None:
        current_user.preferred_currency = profile_data.preferred_currency
    if profile_data.favorite_destinations is not None:
        current_user.favorite_destinations = profile_data.favorite_destinations

    db.commit()
    db.refresh(current_user)
    return current_user

@router.put("/settings", response_model=UserOut)
def update_settings(
    settings_data: UserSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_mock)
):
    """Update user settings (notifications, etc)."""
    if settings_data.notification_settings is not None:
        current_user.notification_settings = settings_data.notification_settings

    db.commit()
    db.refresh(current_user)
    return current_user
