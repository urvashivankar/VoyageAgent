from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    mobile = Column(String, nullable=False)
    
    # Profile & Settings
    profile_picture = Column(String, nullable=True)
    trips_planned = Column(Integer, default=0)
    countries_visited = Column(Integer, default=0)
    travel_days = Column(Integer, default=0)
    money_saved = Column(Float, default=0.0)
    preferred_currency = Column(String, default="INR")
    travel_style = Column(String, nullable=True)
    favorite_destinations = Column(JSON, nullable=True)
    notification_settings = Column(JSON, nullable=True)

    trips = relationship("Trip", back_populates="owner")

class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    destination = Column(String, index=True)
    budget = Column(Float)
    days = Column(Integer)
    travelers = Column(Integer, default=1)
    travel_style = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Trip Management
    is_saved = Column(Boolean, default=False)
    is_favorite = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)

    # AI generated fields
    budget_allocation = Column(JSON, nullable=True)
    hotel_recommendations = Column(JSON, nullable=True)
    travel_tips = Column(JSON, nullable=True)
    total_estimated_cost = Column(Float, nullable=True)

    owner = relationship("User", back_populates="trips")
    itineraries = relationship("Itinerary", back_populates="trip")
    expenses = relationship("Expense", back_populates="trip")

class SavedSelection(Base):
    __tablename__ = "saved_selections"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(String, index=True)
    selection_type = Column(String, index=True)
    item = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class Itinerary(Base):
    __tablename__ = "itineraries"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"))
    day_number = Column(Integer)
    activities = Column(JSON) # Store activities for the day as JSON list

    trip = relationship("Trip", back_populates="itineraries")

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"))
    category = Column(String)
    amount = Column(Float)

    trip = relationship("Trip", back_populates="expenses")
