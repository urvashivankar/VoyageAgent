import random
from .state import TripState
from .llm_config import get_llm, invoke_with_retry
from pydantic import BaseModel, Field
from typing import List
from langchain_core.prompts import PromptTemplate

class Hotel(BaseModel):
    name: str = Field(description="Name of the hotel")
    price: float = Field(description="Estimated price per night")
    rating: float = Field(description="Hotel rating out of 5")
    location: str = Field(description="Specific neighborhood or area")
    amenities: List[str] = Field(description="Top 3-4 amenities (e.g. 'Free WiFi', 'Pool')")
    distance: str = Field(description="Distance from city center or main attraction (e.g. '2 km from center')")
    reason: str = Field(description="Why this hotel fits the user's travel style and budget")
    image: str = Field(description="A descriptive keyword for the hotel to find a placeholder image")

class HotelRecommendations(BaseModel):
    hotels: List[Hotel]

def hotel_agent(state: TripState) -> TripState:
    llm = get_llm().with_structured_output(HotelRecommendations)
    
    # Check if budget_allocation exists, else fallback
    hotel_budget = state.get("budget_allocation", {}).get("hotel", state["budget"] * 0.3)
    avg_nightly_budget = hotel_budget / max(1, state["days"])
    
    prompt = PromptTemplate.from_template(
        "You are an expert hotel recommender. Recommend 3 highly-rated hotels in {destination} "
        "that fit a {travel_style} travel style for {travelers} travelers. "
        "The average nightly budget is around {currency} {avg_nightly_budget:.2f}. "
        "Provide name, price, rating, location, amenities, distance from center, and your reasoning."
    )
    
    chain = prompt | llm
    result = invoke_with_retry(chain, {
        "destination": state["destination"],
        "travel_style": state["travel_style"],
        "travelers": state.get("travelers", 1),
        "currency": state.get("currency", "INR"),
        "avg_nightly_budget": avg_nightly_budget
    })
    
    hotels = []
    for h in result.hotels:
        hd = h.model_dump()
        hd['image'] = f"https://images.unsplash.com/photo-{random.choice(['1566073771259-6a8506099945','1582719508461-905c673771fd','1522708323590-d24dbb6b0267','1596436886108-bc5fb46c1514'])}?q=80&w=1200&auto=format&fit=crop"
        hotels.append(hd)

    state["hotel_recommendations"] = hotels
    return state
