from typing import List, Dict, Any, Optional
import datetime

# Comprehensive Destination Dataset
DESTINATIONS = [
    {
        "id": "guj_ahmedabad",
        "name": "Ahmedabad",
        "state": "Gujarat",
        "category": ["City", "Family Trip"],
        "description": "India's first UNESCO World Heritage City, famous for Gandhi Ashram, textiles, and street food.",
        "best_season": ["October", "November", "December", "January", "February", "March"],
        "avg_budget_inr": 25000,
        "avg_duration_days": 3,
        "hero_image": "https://images.unsplash.com/photo-1616422285623-14ff4e6345ec?q=80&w=1200&auto=format&fit=crop",
        "nearby_attractions": ["Sabarmati Ashram", "Kankaria Lake", "Adalaj Stepwell", "Akshardham Temple"]
    },
    {
        "id": "guj_kutch",
        "name": "Rann of Kutch",
        "state": "Gujarat",
        "category": ["Adventure Destination", "Family Trip"],
        "description": "A massive expanse of white salt desert, especially beautiful during the Rann Utsav.",
        "best_season": ["November", "December", "January", "February"],
        "avg_budget_inr": 35000,
        "avg_duration_days": 4,
        "hero_image": "https://images.unsplash.com/photo-1594958178877-c81ec38bb22d?q=80&w=1200&auto=format&fit=crop",
        "nearby_attractions": ["White Rann", "Kala Dungar", "Dholavira", "Mandvi Beach"]
    },
    {
        "id": "guj_statue_of_unity",
        "name": "Statue of Unity",
        "state": "Gujarat",
        "category": ["Family Trip", "City"],
        "description": "The world's tallest statue, dedicated to Sardar Vallabhbhai Patel, located near Kevadia.",
        "best_season": ["October", "November", "December", "January", "February", "March"],
        "avg_budget_inr": 15000,
        "avg_duration_days": 2,
        "hero_image": "https://images.unsplash.com/photo-1614760822606-d0a0b12bc1a8?q=80&w=1200&auto=format&fit=crop",
        "nearby_attractions": ["Valley of Flowers", "Sardar Sarovar Dam", "Zarwani Waterfall", "Jungle Safari"]
    },
    {
        "id": "raj_jaipur",
        "name": "Jaipur",
        "state": "Rajasthan",
        "category": ["City", "Family Trip", "Luxury Destination"],
        "description": "The Pink City, known for its royal palaces, forts, and vibrant markets.",
        "best_season": ["October", "November", "December", "January", "February", "March"],
        "avg_budget_inr": 30000,
        "avg_duration_days": 3,
        "hero_image": "https://images.unsplash.com/photo-1477587458883-47145ed94245?q=80&w=1200&auto=format&fit=crop",
        "nearby_attractions": ["Amer Fort", "Hawa Mahal", "City Palace", "Jantar Mantar"]
    },
    {
        "id": "raj_udaipur",
        "name": "Udaipur",
        "state": "Rajasthan",
        "category": ["City", "Honeymoon Destination", "Luxury Destination"],
        "description": "The City of Lakes, offering romantic boat rides, stunning palaces, and heritage hotels.",
        "best_season": ["September", "October", "November", "December", "January", "February", "March"],
        "avg_budget_inr": 40000,
        "avg_duration_days": 3,
        "hero_image": "https://images.unsplash.com/photo-1615836245337-f839d7840162?q=80&w=1200&auto=format&fit=crop",
        "nearby_attractions": ["Lake Pichola", "City Palace", "Jag Mandir", "Sajjangarh Fort"]
    },
    {
        "id": "goa_goa",
        "name": "Goa",
        "state": "Goa",
        "category": ["Beach", "Backpacking Destination", "Honeymoon Destination"],
        "description": "India's pocket-sized paradise famous for its beaches, vibrant nightlife, and Portuguese heritage.",
        "best_season": ["October", "November", "December", "January", "February", "March", "September"],
        "avg_budget_inr": 35000,
        "avg_duration_days": 5,
        "hero_image": "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?q=80&w=1200&auto=format&fit=crop",
        "nearby_attractions": ["Baga Beach", "Fort Aguada", "Dudhsagar Falls", "Chapora Fort", "Basilica of Bom Jesus"]
    },
    {
        "id": "ker_munnar",
        "name": "Munnar",
        "state": "Kerala",
        "category": ["Hill Station", "Honeymoon Destination", "Monsoon Escapes"],
        "description": "A tranquil hill station known for its sprawling tea estates, misty hills, and cool climate.",
        "best_season": ["June", "July", "August", "September", "October", "November", "December", "January", "February"],
        "avg_budget_inr": 28000,
        "avg_duration_days": 3,
        "hero_image": "https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?q=80&w=1200&auto=format&fit=crop",
        "nearby_attractions": ["Tea Museum", "Mattupetty Dam", "Eravikulam National Park", "Echo Point"]
    },
    {
        "id": "mah_lonavala",
        "name": "Lonavala",
        "state": "Maharashtra",
        "category": ["Hill Station", "Family Trip", "Monsoon Escapes"],
        "description": "A popular hill station near Mumbai and Pune, especially lush green during the monsoons.",
        "best_season": ["June", "July", "August", "September"],
        "avg_budget_inr": 15000,
        "avg_duration_days": 2,
        "hero_image": "https://images.unsplash.com/photo-1621213032549-33b006cfa024?q=80&w=1200&auto=format&fit=crop",
        "nearby_attractions": ["Tiger's Leap", "Bhushi Dam", "Lonavala Lake", "Karla Caves"]
    },
    {
        "id": "hp_manali",
        "name": "Manali",
        "state": "Himachal Pradesh",
        "category": ["Hill Station", "Adventure Destination", "Honeymoon Destination", "Backpacking Destination"],
        "description": "A high-altitude Himalayan resort town known for backpacking and honeymooning.",
        "best_season": ["March", "April", "May", "June", "September", "October"],
        "avg_budget_inr": 30000,
        "avg_duration_days": 4,
        "hero_image": "https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?q=80&w=1200&auto=format&fit=crop",
        "nearby_attractions": ["Solang Valley", "Rohtang Pass", "Hadimba Temple", "Old Manali"]
    },
    {
        "id": "kas_kashmir",
        "name": "Kashmir",
        "state": "Jammu & Kashmir",
        "category": ["Hill Station", "Honeymoon Destination", "Family Trip"],
        "description": "Paradise on Earth, famous for Dal Lake, Shikara rides, and snow-capped mountains.",
        "best_season": ["March", "April", "May", "June", "September", "October"],
        "avg_budget_inr": 45000,
        "avg_duration_days": 6,
        "hero_image": "https://images.unsplash.com/photo-1595815771614-ade9d6527620?q=80&w=1200&auto=format&fit=crop",
        "nearby_attractions": ["Dal Lake", "Gulmarg", "Pahalgam", "Sonamarg"]
    }
]

def search_destinations(query: str) -> List[Dict[str, Any]]:
    """Autocomplete search by name or state."""
    if not query:
        return []
    
    query = query.lower()
    results = []
    
    # Check if query matches state first for group behavior
    state_matches = [d for d in DESTINATIONS if query in d['state'].lower()]
    
    # If the user typed a state (e.g. "guj", "raj"), return cities in that state
    if state_matches:
        results.extend(state_matches)
    
    # Then check specific names
    name_matches = [d for d in DESTINATIONS if query in d['name'].lower() and d not in results]
    results.extend(name_matches)
    
    # Map to professional dropdown format
    return [
        {
            "id": r["id"],
            "name": r["name"],
            "state": r["state"],
            "category": r["category"][0] if r["category"] else "Destination",
            "hero_image": r["hero_image"]
        }
        for r in results
    ][:8] # Limit to 8 results

def get_destinations_by_category(category: str) -> List[Dict[str, Any]]:
    """Filter destinations by specific category."""
    results = [d for d in DESTINATIONS if category in d["category"]]
    return results

def get_seasonal_recommendations() -> List[Dict[str, Any]]:
    """Recommend destinations based on current month."""
    current_month = datetime.datetime.now().strftime("%B")
    
    results = [d for d in DESTINATIONS if current_month in d["best_season"]]
    
    # Fallback to random if no match
    if not results:
        results = DESTINATIONS[:4]
        
    # Return formatted cards
    return [
        {
            "id": r["id"],
            "name": r["name"],
            "state": r["state"],
            "description": r["description"],
            "hero_image": r["hero_image"],
            "avg_budget": r["avg_budget_inr"],
            "days": r["avg_duration_days"]
        }
        for r in results
    ][:6]

def get_destination_details(name_or_id: str) -> Optional[Dict[str, Any]]:
    """Get full details for a destination."""
    for d in DESTINATIONS:
        if d["id"] == name_or_id or d["name"].lower() == name_or_id.lower():
            return d
    return None
