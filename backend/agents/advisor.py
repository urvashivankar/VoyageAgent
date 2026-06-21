from .state import TripState
from .llm_config import get_llm
from pydantic import BaseModel, Field
from typing import List
from langchain_core.prompts import PromptTemplate

class TravelTips(BaseModel):
    best_season: str = Field(description="Best time of year to visit")
    local_tips: List[str] = Field(description="Useful local tips")
    safety_advice: List[str] = Field(description="Safety advice for the destination")
    packing_suggestions: List[str] = Field(description="What to pack")
    emergency_info: str = Field(description="Emergency numbers or contacts (e.g. 911, 112)")

def advisor_agent(state: TripState) -> TripState:
    llm = get_llm().with_structured_output(TravelTips)
    
    prompt = PromptTemplate.from_template(
        "You are a seasoned travel advisor. The user is traveling to {destination} "
        "for a {travel_style} trip. Provide the best season to visit, local tips, "
        "safety advice, packing suggestions, and local emergency info."
    )
    
    chain = prompt | llm
    result = chain.invoke({
        "destination": state["destination"],
        "travel_style": state["travel_style"]
    })
    
    state["travel_tips"] = result.dict()
    return state
