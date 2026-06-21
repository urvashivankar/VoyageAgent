from fastapi import APIRouter, Query
from typing import List, Dict, Any
from services.destination_service import (
    search_destinations, 
    get_destinations_by_category, 
    get_seasonal_recommendations,
    get_destination_details
)

router = APIRouter(prefix="/destinations", tags=["destinations"])

@router.get("/search")
def search(q: str = Query(..., min_length=1)):
    """Autocomplete search for destinations."""
    return search_destinations(q)

@router.get("/category/{category}")
def by_category(category: str):
    """Get destinations by category (e.g. 'Beach', 'Hill Station')."""
    return get_destinations_by_category(category)

@router.get("/seasonal")
def seasonal_trending():
    """Get destinations recommended for the current month."""
    return get_seasonal_recommendations()

@router.get("/{destination_id}")
def details(destination_id: str):
    """Get full details for a destination."""
    dest = get_destination_details(destination_id)
    if dest:
        return dest
    return {"error": "Destination not found"}
