from langgraph.graph import StateGraph, END
from .state import TripState
from .budget import budget_agent
from .hotel import hotel_agent
from .attraction import attraction_agent
from .itinerary import itinerary_agent
from .expense import expense_agent
from .advisor import advisor_agent

def create_trip_graph():
    workflow = StateGraph(TripState)
    
    # Add nodes
    workflow.add_node("budget", budget_agent)
    workflow.add_node("hotel", hotel_agent)
    workflow.add_node("attraction", attraction_agent)
    workflow.add_node("itinerary", itinerary_agent)
    workflow.add_node("expense", expense_agent)
    workflow.add_node("advisor", advisor_agent)
    
    # Add edges
    workflow.set_entry_point("budget")
    workflow.add_edge("budget", "hotel")
    workflow.add_edge("hotel", "attraction")
    workflow.add_edge("attraction", "itinerary")
    workflow.add_edge("itinerary", "expense")
    workflow.add_edge("expense", "advisor")
    workflow.add_edge("advisor", END)
    
    # Compile graph
    return workflow.compile()
