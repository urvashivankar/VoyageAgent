from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    mobile: str

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    
    # Profile & Settings
    profile_picture: Optional[str] = None
    trips_planned: int = 0
    countries_visited: int = 0
    travel_days: int = 0
    money_saved: float = 0.0
    preferred_currency: str = "INR"
    travel_style: Optional[str] = None
    favorite_destinations: Optional[List[str]] = None
    notification_settings: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    profile_picture: Optional[str] = None
    travel_style: Optional[str] = None
    preferred_currency: Optional[str] = None
    favorite_destinations: Optional[List[str]] = None

class UserSettingsUpdate(BaseModel):
    notification_settings: Optional[Dict[str, Any]] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class TripCreate(BaseModel):
    destination: str
    budget: float
    days: int
    travelers: int = 1
    travel_style: str
    currency: Optional[str] = "INR"

class TripUpdate(BaseModel):
    is_saved: Optional[bool] = None
    is_favorite: Optional[bool] = None
    is_deleted: Optional[bool] = None

class ExpenseOut(BaseModel):
    id: int
    category: str
    amount: float

    class Config:
        from_attributes = True

class ItineraryOut(BaseModel):
    id: int
    day_number: int
    activities: List[Dict[str, Any]]

    class Config:
        from_attributes = True

class TripOut(BaseModel):
    id: int
    destination: str
    budget: float
    days: int
    travelers: int
    travel_style: str
    created_at: datetime
    
    # Trip Management
    is_saved: bool
    is_favorite: bool

    # AI-generated results
    budget_allocation: Optional[Dict[str, float]] = None
    hotel_recommendations: Optional[List[Dict[str, Any]]] = None
    travel_tips: Optional[Dict[str, Any]] = None
    total_estimated_cost: Optional[float] = None
    itineraries: List[ItineraryOut] = []
    expenses: List[ExpenseOut] = []

    class Config:
        from_attributes = True
