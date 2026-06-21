from .state import TripState
from .llm_config import get_llm
from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
import json

class ExpenseSummary(BaseModel):
    total_cost: float = Field(description="Total estimated cost for the whole trip")
    breakdown_notes: str = Field(description="Brief explanation of the calculation")

def expense_agent(state: TripState) -> TripState:
    llm = get_llm().with_structured_output(ExpenseSummary)
    
    budget_alloc = state.get("budget_allocation", {})
    hotels = state.get("hotel_recommendations", [])
    attractions = state.get("attractions", [])
    
    prompt = PromptTemplate.from_template(
        "You are a travel expense accountant. Review the following details for a {days}-day trip to {destination}:\n"
        "Budget Allocation: {budget_alloc}\n"
        "Recommended Hotels: {hotels}\n"
        "Attractions: {attractions}\n\n"
        "Calculate a realistic total estimated cost (which could be slightly different from the initial budget) "
        "based on the actual recommended items. Provide the total and a brief note."
    )
    
    chain = prompt | llm
    result = chain.invoke({
        "days": state["days"],
        "destination": state["destination"],
        "budget_alloc": json.dumps(budget_alloc),
        "hotels": json.dumps(hotels),
        "attractions": json.dumps(attractions)
    })
    
    state["total_estimated_cost"] = result.total_cost
    # Optionally store the note as well, but state expects total_estimated_cost
    return state
