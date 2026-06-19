import math
from typing import List
from app.schemas import Diner, Restaurant

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on the Earth
    in miles using the Haversine formula.
    """
    # Earth's radius in miles
    R = 3958.8
    
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    
    return R * c

def filter_restaurants(
    restaurants: List[Restaurant],
    diners: List[Diner],
    user_lat: float,
    user_lon: float,
    max_distance_miles: float
) -> List[Restaurant]:
    """
    Filter restaurants by distance and exclude any that match active diner vetoes.
    """
    # 1. Collect all veto tags from active diners
    active_vetoes = set()
    for diner in diners:
        if diner.is_active:
            for dislike in diner.dislikes:
                active_vetoes.add(dislike.strip().lower())
                
    filtered_list = []
    
    for restaurant in restaurants:
        # 2. Check distance
        dist = haversine_distance(user_lat, user_lon, restaurant.latitude, restaurant.longitude)
        if dist > max_distance_miles:
            continue
            
        # 3. Check vetoes
        # Compile all tags for this restaurant to check against vetoes
        restaurant_tags = {tag.strip().lower() for tag in restaurant.disliked_tags}
        if restaurant.cuisine:
            restaurant_tags.add(restaurant.cuisine.strip().lower())
            
        # If any of the restaurant's tags match an active diner's veto, exclude it
        if restaurant_tags.intersection(active_vetoes):
            continue
            
        filtered_list.append(restaurant)
        
    return filtered_list