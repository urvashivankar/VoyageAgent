import random
from .state import TripState
from .llm_config import get_llm, invoke_with_retry
from pydantic import BaseModel, Field
from typing import List
from langchain_core.prompts import PromptTemplate

class Attraction(BaseModel):
    name: str = Field(description="Name of the attraction")
    category: str = Field(description="Historical, Nature, Adventure, Shopping, Food, Relaxation, etc.")
    description: str = Field(description="Short engaging description of the attraction")
    estimated_cost: float = Field(description="Estimated entry fee or cost per person")
    location: str = Field(description="Specific neighborhood, area, or distance from center")
    best_time: str = Field(description="Best time of day to visit (e.g., Early Morning, Sunset)")
    reason: str = Field(description="Why this attraction is recommended for this user's travel style")
    image: str = Field(description="A descriptive keyword for the attraction to find a placeholder image")

class AttractionRecommendations(BaseModel):
    attractions: List[Attraction]

def attraction_agent(state: TripState) -> TripState:
    llm = get_llm().with_structured_output(AttractionRecommendations)
    
    prompt = PromptTemplate.from_template(
        "You are a local tour guide in {destination}. Recommend around 8-10 attractions "
        "suitable for a {travel_style} traveler staying for {days} days. "
        "Categorize them properly and provide estimated entry costs in {currency}. "
        "Include location details, best time to visit, and your reasoning."
    )
    
    chain = prompt | llm
    result = invoke_with_retry(chain, {
        "destination": state["destination"],
        "travel_style": state["travel_style"],
        "days": state["days"],
        "currency": state.get("currency", "INR")
    })
    
    attractions = []
    for a in result.attractions:
        ad = a.model_dump()
        ad['image'] = f"https://images.unsplash.com/photo-{random.choice(['1548013146-72479768bada','1570168007204-dfb528c6958f','1501004318641-b39e6451bec6','1625398407796-82650a8c135f'])}?q=80&w=1200&auto=format&fit=crop"
        # Map some common UI icons based on category
        cat = ad['category'].lower()
        if 'beach' in cat or 'relax' in cat: ad['icon'] = 'waves'
        elif 'history' in cat or 'heritage' in cat: ad['icon'] = 'landmark'
        elif 'nature' in cat: ad['icon'] = 'mountain'
        elif 'shop' in cat: ad['icon'] = 'shopping-bag'
        elif 'food' in cat: ad['icon'] = 'utensils'
        else: ad['icon'] = 'camera'
        attractions.append(ad)

    state["attractions"] = attractions
    return state
