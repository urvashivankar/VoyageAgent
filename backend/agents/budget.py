import json
from .state import TripState
from .llm_config import get_llm, invoke_with_retry
from pydantic import BaseModel
from langchain_core.prompts import PromptTemplate

class BudgetOutput(BaseModel):
    trip_type: str
    feasibility: str
    hotel: float
    food: float
    transport: float
    activities: float
    emergency: float

def budget_agent(state: TripState) -> TripState:
    llm = get_llm().with_structured_output(BudgetOutput)
    
    prompt = PromptTemplate.from_template(
        "You are an expert travel budget planner. The user wants to travel to {destination} "
        "for {days} days with {travelers} travelers. Their total budget is {currency} {budget}. "
        "Their travel style is {travel_style}. "
        "First, determine if the trip is 'Domestic' (within India, assuming user is from India unless destination implies otherwise) or 'International'. "
        "Second, evaluate if the total budget is feasible for this destination, duration, and number of travelers. "
        "Classify the feasibility as one of: 'Excellent', 'Good', 'Tight', 'Insufficient'. "
        "Finally, allocate the budget into these categories: hotel, food, transport, activities, emergency. "
        "Ensure the sum equals the total budget and it's realistic for {destination}."
    )
    
    chain = prompt | llm
    result = invoke_with_retry(chain, {
        "destination": state["destination"],
        "days": state["days"],
        "budget": state["budget"],
        "travelers": state.get("travelers", 1),
        "currency": state.get("currency", "INR"),
        "travel_style": state["travel_style"]
    })
    
    state["trip_type"] = result.trip_type
    state["budget_feasibility"] = result.feasibility
    state["budget_allocation"] = {
        "hotel": result.hotel,
        "food": result.food,
        "transport": result.transport,
        "activities": result.activities,
        "emergency": result.emergency
    }
    return state
