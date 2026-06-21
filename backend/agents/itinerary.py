import json
from .state import TripState
from .llm_config import get_llm, invoke_with_retry
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from langchain_core.prompts import PromptTemplate

class DailyActivity(BaseModel):
    time: str = Field(description="Time of day (Morning, Afternoon, Evening)")
    start_time: str = Field(description="Suggested start time (e.g., 09:00 AM)")
    activity: str = Field(description="Name of the place or attraction")
    title: str = Field(description="Short engaging title for the activity")
    location: str = Field(description="Specific neighborhood or area")
    description: str = Field(description="What to do there, avoiding generic phrases")
    duration: str = Field(description="Expected duration (e.g., 2 hours)")
    travel_time: str = Field(description="Estimated travel time from previous location")
    cost: float = Field(description="Estimated cost/entry fee for this activity")
    google_maps_link: str = Field(description="A google maps search link for the location")

class DailyItinerary(BaseModel):
    day: int = Field(description="Day number")
    theme: str = Field(description="Theme for the day (e.g., Historical Exploration)")
    activities: List[DailyActivity]

class ItineraryOutput(BaseModel):
    days: List[DailyItinerary]

def itinerary_agent(state: TripState) -> TripState:
    llm = get_llm().with_structured_output(ItineraryOutput)
    
    attractions_str = json.dumps(state.get("attractions", []), indent=2)
    
    prompt = PromptTemplate.from_template(
        "You are an expert itinerary planner. Create a {days}-day itinerary for {destination} "
        "tailored for a {travel_style} travel style for {travelers} travelers.\n"
        "Incorporate the following attractions if possible:\n{attractions}\n"
        "Strict Requirements:\n"
        "- Provide exactly 3 activities per day: Morning, Afternoon, Evening.\n"
        "- Avoid generic descriptions like 'enjoy the view' or 'explore the city'. Be specific about what to do, eat, or see.\n"
        "- Include realistic travel times between locations.\n"
        "- Provide a Google Maps search URL (e.g. https://www.google.com/maps/search/?api=1&query=Location+Name).\n"
    )
    
    chain = prompt | llm
    result = invoke_with_retry(chain, {
        "destination": state["destination"],
        "days": state["days"],
        "travelers": state.get("travelers", 1),
        "travel_style": state["travel_style"],
        "attractions": attractions_str
    })
    
    state["itinerary"] = [day.model_dump() for day in result.days]
    return state
