from typing import TypedDict, List, Dict, Any, Optional

class TripState(TypedDict):
    # Inputs
    destination: str
    budget: float
    days: int
    travelers: int
    travel_style: str
    currency: str
    
    # Outputs of agents
    trip_type: Optional[str] # Domestic vs International
    budget_feasibility: Optional[str] # Excellent, Good, Tight, Insufficient
    budget_allocation: Optional[Dict[str, float]]
    hotel_recommendations: Optional[List[Dict[str, Any]]]
    attractions: Optional[List[Dict[str, Any]]]
    itinerary: Optional[List[Dict[str, Any]]]
    total_estimated_cost: Optional[float]
    travel_tips: Optional[Dict[str, Any]]
