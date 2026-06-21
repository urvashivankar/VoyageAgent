import os
from datetime import datetime
from typing import Any, Dict, List
from uuid import uuid4

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.schemas import TripCreate
from database.database import get_db
from database.models import SavedSelection

router = APIRouter(prefix="/trips", tags=["trips"])
AI_MODE = os.getenv("TRIPPILOT_AI_MODE", "local").strip().lower()


class SaveSelectionRequest(BaseModel):
    type: str
    item: Dict[str, Any]

try:
    from agents.graph import create_trip_graph

    graph = create_trip_graph()
    AI_AVAILABLE = True
except Exception as e:
    print(f"AI graph unavailable, using local trip generator: {e}")
    AI_AVAILABLE = False
    graph = None


def _split_destination(destination: str) -> str:
    return destination.split(",")[0].strip() or destination.strip()


def _agent_status(name: str, status: str = "completed", detail: str = "") -> Dict[str, str]:
    return {"agent": name, "status": status, "detail": detail}


DESTINATION_GUIDES: Dict[str, Dict[str, Any]] = {
    "dubai": {
        "hero_image": "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?q=80&w=1920&auto=format&fit=crop",
        "currency": "INR",
        "attractions": [
            {
                "name": "Burj Khalifa",
                "category": "Landmark",
                "location": "Downtown Dubai",
                "description": "Ride up the world's tallest tower for skyline views over Downtown Dubai and the coastline.",
                "estimated_cost": 3750,
                "travel_time": "15-25 min from central hotels",
                "icon": "building-2",
                "image": "https://images.unsplash.com/photo-1582672060674-bc2bd808a8b5?q=80&w=1200&auto=format&fit=crop",
            },
            {
                "name": "Dubai Mall",
                "category": "Shopping",
                "location": "Downtown Dubai",
                "description": "Explore flagship stores, dining, the aquarium area, and the evening fountain promenade.",
                "estimated_cost": 1700,
                "travel_time": "5 min walk from Burj Khalifa",
                "icon": "shopping-bag",
                "image": "https://images.unsplash.com/photo-1581541234269-03d5d85764b5?q=80&w=1200&auto=format&fit=crop",
            },
            {
                "name": "Palm Jumeirah",
                "category": "Luxury",
                "location": "Palm Jumeirah",
                "description": "Visit the palm-shaped island for beach clubs, Atlantis views, and premium waterfront dining.",
                "estimated_cost": 2900,
                "travel_time": "25-35 min from Downtown Dubai",
                "icon": "palmtree",
                "image": "https://images.unsplash.com/photo-1580674684081-7617fbf3d745?q=80&w=1200&auto=format&fit=crop",
            },
            {
                "name": "Museum of the Future",
                "category": "Museum",
                "location": "Sheikh Zayed Road",
                "description": "A futuristic museum with immersive exhibits on space, wellness, robotics, and cities of tomorrow.",
                "estimated_cost": 3350,
                "travel_time": "10-15 min from Downtown Dubai",
                "icon": "sparkles",
                "image": "https://images.unsplash.com/photo-1661347333274-85414d235bc6?q=80&w=1200&auto=format&fit=crop",
            },
            {
                "name": "Dubai Marina",
                "category": "Waterfront",
                "location": "Dubai Marina",
                "description": "Walk the marina promenade, take a dhow cruise, and enjoy the skyline after sunset.",
                "estimated_cost": 2500,
                "travel_time": "25-35 min from Downtown Dubai",
                "icon": "sailboat",
                "image": "https://images.unsplash.com/photo-1526495124232-a04e1849168c?q=80&w=1200&auto=format&fit=crop",
            },
            {
                "name": "Desert Safari",
                "category": "Adventure",
                "location": "Dubai Desert Conservation area",
                "description": "An evening desert experience with dune bashing, camel rides, dinner, and live performances.",
                "estimated_cost": 5850,
                "travel_time": "45-60 min from city hotels",
                "icon": "sunset",
                "image": "https://images.unsplash.com/photo-1509316785289-025f5b846b35?q=80&w=1200&auto=format&fit=crop",
            },
            {
                "name": "Al Fahidi Historical Neighbourhood",
                "category": "Culture",
                "location": "Bur Dubai",
                "description": "Explore restored wind-tower houses, galleries, creekside lanes, and traditional Emirati culture.",
                "estimated_cost": 850,
                "travel_time": "20-30 min from Downtown Dubai",
                "icon": "landmark",
                "image": "https://images.unsplash.com/photo-1546412414-e1885259563a?q=80&w=1200&auto=format&fit=crop",
            },
            {
                "name": "Jumeirah Beach",
                "category": "Relaxation",
                "location": "Jumeirah",
                "description": "Slow down with beach time, Burj Al Arab views, and an easy coastal cafe stop.",
                "estimated_cost": 1250,
                "travel_time": "20-30 min from Downtown Dubai",
                "icon": "waves",
                "image": "https://images.unsplash.com/photo-1526772662000-3f88f10405ff?q=80&w=1200&auto=format&fit=crop",
            },
        ],
    },
    "goa": {
        "hero_image": "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?q=80&w=1920&auto=format&fit=crop",
        "currency": "INR",
        "attractions": [
            {
                "name": "Baga Beach",
                "category": "Beach",
                "location": "North Goa",
                "description": "Classic Goa beach energy with shacks, watersports, and easy evening dining.",
                "estimated_cost": 1200,
                "duration": "2-3 hr",
                "distance": "18 km from Panjim",
                "rating": 4.4,
                "travel_time": "20-40 min from North Goa hotels",
                "icon": "waves",
                "image": "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?q=80&w=1200&auto=format&fit=crop",
            },
            {
                "name": "Anjuna Beach",
                "category": "Beach",
                "location": "North Goa",
                "description": "A lively beach known for sunset views, flea-market energy, cafes, and casual nightlife.",
                "estimated_cost": 1000,
                "duration": "2 hr",
                "distance": "21 km from Panjim",
                "rating": 4.3,
                "travel_time": "20-30 min from Baga",
                "icon": "waves",
                "image": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?q=80&w=1200&auto=format&fit=crop",
            },
            {
                "name": "Vagator Beach",
                "category": "Beach",
                "location": "North Goa",
                "description": "Dramatic red cliffs, sunset points, and a calmer beach stop close to Chapora.",
                "estimated_cost": 900,
                "duration": "2 hr",
                "distance": "22 km from Panjim",
                "rating": 4.5,
                "travel_time": "15-20 min from Anjuna",
                "icon": "sunset",
                "image": "https://images.unsplash.com/photo-1552733407-5d5c46c3bb3b?q=80&w=1200&auto=format&fit=crop",
            },
            {
                "name": "Fort Aguada",
                "category": "Historical",
                "location": "Candolim",
                "description": "A Portuguese-era fort with sea views and relaxed photo stops.",
                "estimated_cost": 300,
                "duration": "1-1.5 hr",
                "distance": "15 km from Panjim",
                "rating": 4.2,
                "travel_time": "20-30 min from Baga",
                "icon": "landmark",
                "image": "https://images.unsplash.com/photo-1570168007204-dfb528c6958f?q=80&w=1200&auto=format&fit=crop",
            },
            {
                "name": "Dudhsagar Falls",
                "category": "Nature",
                "location": "Mollem",
                "description": "A dramatic waterfall day trip with forest scenery and jeep access in season.",
                "estimated_cost": 3500,
                "duration": "6-8 hr",
                "distance": "60 km from Panjim",
                "rating": 4.6,
                "travel_time": "2-3 hr from coastal Goa",
                "icon": "mountain",
                "image": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?q=80&w=1200&auto=format&fit=crop",
            },
            {
                "name": "Dona Paula",
                "category": "Viewpoint",
                "location": "Panjim",
                "description": "A breezy waterfront viewpoint with sea views, photo stops, and quick access from Panjim.",
                "estimated_cost": 500,
                "duration": "1 hr",
                "distance": "7 km from Panjim",
                "rating": 4.1,
                "travel_time": "15-20 min from Panjim",
                "icon": "binoculars",
                "image": "https://images.unsplash.com/photo-1548013146-72479768bada?q=80&w=1200&auto=format&fit=crop",
            },
            {
                "name": "Mandovi Cruise",
                "category": "Cruise",
                "location": "Panjim",
                "description": "Evening river cruise with music, city lights, and views along the Mandovi.",
                "estimated_cost": 1500,
                "duration": "1.5-2 hr",
                "distance": "2 km from Panjim",
                "rating": 4.2,
                "travel_time": "10-15 min from central Panjim",
                "icon": "ship",
                "image": "https://images.unsplash.com/photo-1548574505-5e239809ee19?q=80&w=1200&auto=format&fit=crop",
            },
            {
                "name": "Thalassa",
                "category": "Dining",
                "location": "Siolim",
                "description": "Iconic Greek-style restaurant loved for sunset dining, music, and river views.",
                "estimated_cost": 2500,
                "duration": "2 hr",
                "distance": "24 km from Panjim",
                "rating": 4.5,
                "travel_time": "35-45 min from Panjim",
                "icon": "utensils",
                "image": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?q=80&w=1200&auto=format&fit=crop",
            },
            {
                "name": "Fontainhas",
                "category": "Culture",
                "location": "Panjim",
                "description": "Colorful Latin Quarter lanes, cafes, galleries, and heritage homes.",
                "estimated_cost": 700,
                "duration": "1.5-2 hr",
                "distance": "1 km from Panjim",
                "rating": 4.4,
                "travel_time": "35-50 min from North Goa",
                "icon": "palette",
                "image": "https://images.unsplash.com/photo-1590001155093-a3c66ab0c3ff?q=80&w=1200&auto=format&fit=crop",
            },
            {
                "name": "Chapora Fort",
                "category": "Historical",
                "location": "Vagator",
                "description": "A hilltop fort with wide views over Vagator, Chapora River, and the Arabian Sea.",
                "estimated_cost": 300,
                "duration": "1 hr",
                "distance": "21 km from Panjim",
                "rating": 4.3,
                "travel_time": "15 min from Vagator Beach",
                "icon": "landmark",
                "image": "https://images.unsplash.com/photo-1589308454676-22f51e4bb31a?q=80&w=1200&auto=format&fit=crop",
            },
            {
                "name": "Basilica of Bom Jesus",
                "category": "Heritage",
                "location": "Old Goa",
                "description": "UNESCO-listed baroque church and one of Goa's most important heritage landmarks.",
                "estimated_cost": 200,
                "duration": "1 hr",
                "distance": "10 km from Panjim",
                "rating": 4.5,
                "travel_time": "20-25 min from Panjim",
                "icon": "church",
                "image": "https://images.unsplash.com/photo-1625398407796-82650a8c135f?q=80&w=1200&auto=format&fit=crop",
            },
            {
                "name": "Sahakari Spice Farm",
                "category": "Nature",
                "location": "Ponda",
                "description": "Guided spice plantation visit with Goan lunch and a slower inland contrast to the beaches.",
                "estimated_cost": 1200,
                "duration": "3 hr",
                "distance": "30 km from Panjim",
                "rating": 4.2,
                "travel_time": "45-60 min from Panjim",
                "icon": "leaf",
                "image": "https://images.unsplash.com/photo-1501004318641-b39e6451bec6?q=80&w=1200&auto=format&fit=crop",
            },
            {
                "name": "Arambol Beach",
                "category": "Beach",
                "location": "North Goa",
                "description": "Bohemian beach with music circles, casual cafes, and a relaxed northern Goa feel.",
                "estimated_cost": 1000,
                "duration": "2-3 hr",
                "distance": "35 km from Panjim",
                "rating": 4.4,
                "travel_time": "60-75 min from Panjim",
                "icon": "waves",
                "image": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?q=80&w=1200&auto=format&fit=crop",
            },
            {
                "name": "Palolem Beach",
                "category": "Beach",
                "location": "South Goa",
                "description": "Crescent-shaped South Goa beach suited for kayaking, easy cafes, and quieter evenings.",
                "estimated_cost": 1500,
                "duration": "3 hr",
                "distance": "70 km from Panjim",
                "rating": 4.6,
                "travel_time": "2 hr from Panjim",
                "icon": "umbrella",
                "image": "https://images.unsplash.com/photo-1519046904884-53103b34b206?q=80&w=1200&auto=format&fit=crop",
            },
            {
                "name": "Reis Magos Fort",
                "category": "Historical",
                "location": "Verem",
                "description": "Restored riverside fort with galleries, Mandovi views, and a calmer heritage stop.",
                "estimated_cost": 400,
                "duration": "1-1.5 hr",
                "distance": "8 km from Panjim",
                "rating": 4.4,
                "travel_time": "20 min from Panjim",
                "icon": "castle",
                "image": "https://images.unsplash.com/photo-1570168007204-dfb528c6958f?q=80&w=1200&auto=format&fit=crop",
            },
        ],
    },
}


DEFAULT_ATTRACTION_IMAGES = [
    "https://images.unsplash.com/photo-1488646953014-85cb44e25828?q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1526772662000-3f88f10405ff?q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?q=80&w=1200&auto=format&fit=crop",
]


def _destination_guide(city: str) -> Dict[str, Any]:
    key = city.lower()
    for name, guide in DESTINATION_GUIDES.items():
        if name in key:
            return guide
    return {
        "hero_image": "https://images.unsplash.com/photo-1488646953014-85cb44e25828?q=80&w=1920&auto=format&fit=crop",
        "currency": "INR",
        "attractions": [
            {
                "name": f"{city} Heritage Quarter",
                "category": "Culture",
                "location": city,
                "description": f"Start with the old-town streets, local architecture, and the story of {city}.",
                "estimated_cost": 1000,
                "travel_time": "15-25 min from central hotels",
                "icon": "landmark",
                "image": DEFAULT_ATTRACTION_IMAGES[0],
            },
            {
                "name": f"{city} Signature Viewpoint",
                "category": "Nature",
                "location": city,
                "description": f"A scenic stop for orientation, photos, and a relaxed view across {city}.",
                "estimated_cost": 850,
                "travel_time": "20-30 min from the heritage quarter",
                "icon": "mountain",
                "image": DEFAULT_ATTRACTION_IMAGES[1],
            },
            {
                "name": f"{city} Local Market",
                "category": "Food",
                "location": city,
                "description": "Taste regional snacks, browse local crafts, and keep the afternoon flexible.",
                "estimated_cost": 1500,
                "travel_time": "10-20 min from central hotels",
                "icon": "shopping-bag",
                "image": DEFAULT_ATTRACTION_IMAGES[2],
            },
            {
                "name": f"{city} Evening Promenade",
                "category": "Relaxation",
                "location": city,
                "description": "End with an easy walk, dinner, and a low-pressure evening close to your stay.",
                "estimated_cost": 1700,
                "travel_time": "15-25 min from the market district",
                "icon": "moon",
                "image": DEFAULT_ATTRACTION_IMAGES[3],
            },
        ],
    }


def _local_trip_state(trip_data: TripCreate, reason: str = "Local generator") -> Dict[str, Any]:
    """Deterministic local fallback used when Gemini is unavailable or quota-limited."""
    budget = float(trip_data.budget)
    days = max(1, int(trip_data.days))
    dest = trip_data.destination.strip()
    city = _split_destination(dest)
    style = trip_data.travel_style.strip() or "Relaxing"
    guide = _destination_guide(city)

    budget_allocation = {
        "hotel": round(budget * 0.38, 2),
        "food": round(budget * 0.22, 2),
        "transport": round(budget * 0.15, 2),
        "activities": round(budget * 0.20, 2),
        "emergency": round(budget * 0.05, 2),
    }

    hotel_nightly = round(budget_allocation["hotel"] / days, 2)
    hotel_recommendations = [
        {
            "name": f"{city} Central Stay",
            "price": hotel_nightly,
            "price_per_night": hotel_nightly,
            "rating": 4.5,
            "location": f"Central {city}",
            "reason": f"Convenient base for a {style.lower()} trip with easy access to major sights.",
            "description": f"Convenient base for a {style.lower()} trip with easy access to major sights.",
            "amenities": ["Free WiFi", "Breakfast", "Transit nearby"],
        },
        {
            "name": f"{city} Boutique Inn",
            "price": round(hotel_nightly * 0.85, 2),
            "price_per_night": round(hotel_nightly * 0.85, 2),
            "rating": 4.3,
            "location": f"Old town / local neighborhood, {city}",
            "reason": "Good value option with a more local feel.",
            "description": "Good value option with a more local feel.",
            "amenities": ["Local dining nearby", "Comfort rooms", "Front desk support"],
        },
        {
            "name": f"{city} Comfort Hotel",
            "price": round(hotel_nightly * 1.05, 2),
            "price_per_night": round(hotel_nightly * 1.05, 2),
            "rating": 4.4,
            "location": f"Tourist district, {city}",
            "reason": "Balanced comfort and access for first-time visitors.",
            "description": "Balanced comfort and access for first-time visitors.",
            "amenities": ["Airport transfers", "Room service", "Tour desk"],
        },
    ]

    attractions = guide["attractions"]

    itinerary: List[Dict[str, Any]] = []
    for day in range(1, days + 1):
        day_activities = []
        day_start = (day - 1) * 3
        for offset, time_label in enumerate(("Morning", "Afternoon", "Evening")):
            activity_index = day_start + offset
            if activity_index < len(attractions):
                activity = attractions[activity_index]
            else:
                base_attraction = attractions[activity_index % len(attractions)]
                activity = {
                    "name": base_attraction["name"],
                    "category": base_attraction["category"],
                    "location": base_attraction["location"],
                    "description": base_attraction["description"],
                    "estimated_cost": round(budget_allocation["activities"] / max(days * 3, 1), 2),
                    "travel_time": base_attraction["travel_time"],
                    "icon": base_attraction["icon"],
                    "image": base_attraction["image"],
                }
            day_activities.append(
                {
                    "time": time_label,
                    "start_time": ["09:00 AM", "01:30 PM", "06:30 PM"][offset],
                    "activity": activity["name"],
                    "title": activity["name"],
                    "location": activity["location"],
                    "category": activity["category"],
                    "description": activity["description"],
                    "travel_time": activity["travel_time"],
                    "estimated_cost": activity["estimated_cost"],
                    "cost": activity["estimated_cost"],
                    "icon": activity["icon"],
                    "image": activity["image"],
                }
            )
        itinerary.append(
            {
                "day": day,
                "theme": f"{style} route through {city}: " + ", ".join(item["title"] for item in day_activities),
                "activities": day_activities,
            }
        )

    reasoning = [
        f"Optimized for your {guide['currency']} {budget:,.0f} budget with a clear hotel, food, transport, activities, and emergency split.",
        "Minimized travel distance by grouping nearby landmarks into the same day where possible.",
        f"Prioritized {style.lower()} experiences while still covering the destination's must-see attractions.",
        "Balanced sightseeing, meals, photo stops, and evening recovery time so the plan feels realistic.",
    ]

    return {
        "id": uuid4().hex,
        "destination": dest,
        "budget": budget,
        "days": days,
        "travelers": int(trip_data.travelers),
        "travel_style": style,
        "created_at": datetime.utcnow().isoformat(),
        "hero_image": guide["hero_image"],
        "currency": guide["currency"],
        "trip_type": "Domestic",
        "budget_feasibility": "Good",
        "budget_allocation": budget_allocation,
        "hotel_recommendations": hotel_recommendations,
        "attractions": attractions,
        "itinerary": itinerary,
        "total_estimated_cost": round(sum(budget_allocation.values()), 2),
        "travel_tips": {
            "weather_forecast": f"Expect destination-specific weather swings in {city}; check the 7-day forecast before packing.",
            "best_season": "October to March is usually the most comfortable season for Indian coastal and city breaks.",
            "safety_score": 8.2,
            "local_tips": [
                f"Keep your first day in {city} flexible for arrival delays.",
                "Book popular attractions ahead during weekends and holidays.",
                "Keep a small emergency buffer separate from your main spending money.",
            ],
            "local_transport": "Use registered taxis, app cabs where available, hotel transfers, and pre-negotiated day rentals for longer routes.",
            "safety_advice": [
                "Use registered transport or well-reviewed ride apps.",
                "Keep digital and offline copies of important documents.",
                "Share your itinerary with someone you trust.",
            ],
            "packing_suggestions": [
                "Comfortable walking shoes",
                "Portable charger",
                "Weather-appropriate layers",
                "Reusable water bottle",
            ],
            "emergency_contacts": ["India emergency: 112", "Police: 100", "Ambulance: 108", "Tourist helpline: 1363"],
            "emergency_info": "Save local emergency numbers before departure.",
        },
        "ai_reasoning": reasoning,
        "agent_status": [
            _agent_status("Budget Agent", detail="Budget split created locally."),
            _agent_status("Hotel Agent", detail="Hotel suggestions created locally."),
            _agent_status("Attraction Agent", detail="Attractions created locally."),
            _agent_status("Itinerary Agent", detail="Day-by-day plan created locally."),
            _agent_status("Expense Agent", detail="Estimated total calculated locally."),
            _agent_status("Travel Advisor Agent", detail="Travel tips created locally."),
        ],
        "generation_mode": "local",
        "generation_note": reason,
    }


def _normalize_ai_state(trip_data: TripCreate, state: Dict[str, Any]) -> Dict[str, Any]:
    state = dict(state)
    state.update(
        {
            "id": uuid4().hex,
            "destination": trip_data.destination,
            "budget": float(trip_data.budget),
            "days": int(trip_data.days),
            "travelers": int(trip_data.travelers),
            "travel_style": trip_data.travel_style,
            "created_at": datetime.utcnow().isoformat(),
            "generation_mode": "ai",
            "generation_note": "Generated by LangGraph agents with Gemini.",
            "agent_status": [
                _agent_status("Budget Agent"),
                _agent_status("Hotel Agent"),
                _agent_status("Attraction Agent"),
                _agent_status("Itinerary Agent"),
                _agent_status("Expense Agent"),
                _agent_status("Travel Advisor Agent"),
            ],
        }
    )
    return state


def _generate_trip_state(trip_data: TripCreate) -> Dict[str, Any]:
    initial_state = {
        "destination": trip_data.destination,
        "budget": trip_data.budget,
        "days": trip_data.days,
        "travelers": trip_data.travelers,
        "travel_style": trip_data.travel_style,
        "currency": trip_data.currency or "INR",
        "trip_type": None,
        "budget_feasibility": None,
        "budget_allocation": None,
        "hotel_recommendations": None,
        "attractions": None,
        "itinerary": None,
        "total_estimated_cost": None,
        "travel_tips": None,
    }

    if AI_MODE == "ai" and AI_AVAILABLE and graph:
        try:
            return _normalize_ai_state(trip_data, graph.invoke(initial_state))
        except Exception as e:
            print(f"AI generation failed, using local trip generator: {e}")
            return _local_trip_state(trip_data, reason=f"AI unavailable: {e}")

    return _local_trip_state(trip_data)


@router.post("/")
def create_trip(trip_data: TripCreate):
    return _generate_trip_state(trip_data)


@router.get("/")
def get_user_trips():
    return []


@router.get("/health")
def agent_health():
    return {
        "graph_imported": AI_AVAILABLE,
        "graph_compiled": graph is not None,
        "ai_mode": AI_MODE,
        "live_ai_enabled": AI_MODE == "ai" and AI_AVAILABLE and graph is not None,
        "storage": "browser localStorage with API-backed saved selections",
        "database": "SQLite saved_selections enabled",
        "agents": [
            "Budget Agent",
            "Hotel Agent",
            "Attraction Agent",
            "Itinerary Agent",
            "Expense Agent",
            "Travel Advisor Agent",
        ],
    }


@router.post("/{trip_id}/save-selection")
def save_selection(trip_id: str, payload: SaveSelectionRequest, db: Session = Depends(get_db)):
    selection = SavedSelection(
        trip_id=trip_id,
        selection_type=payload.type,
        item=payload.item,
    )
    db.add(selection)
    db.commit()
    db.refresh(selection)
    return {"id": selection.id, "trip_id": trip_id, "type": payload.type, "item": payload.item}


@router.get("/saved-selections")
def saved_selections(db: Session = Depends(get_db)):
    rows = db.query(SavedSelection).order_by(SavedSelection.created_at.desc()).all()
    return [
        {
            "id": row.id,
            "trip_id": row.trip_id,
            "type": row.selection_type,
            "item": row.item,
            "created_at": row.created_at.isoformat(),
        }
        for row in rows
    ]
