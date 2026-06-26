import httpx
from typing import List
from datetime import datetime
from app.config import settings
from app.schemas import Restaurant

def format_time(time_str: str) -> str:
    try:
        dt = datetime.strptime(time_str, "%H%M")
        return dt.strftime("%I:%M %p").lstrip("0")
    except Exception:
        return time_str

def fetch_live_restaurants(lat: float, lon: float, max_dist_miles: float) -> List[Restaurant]:
    """
    Fetches up to 20 restaurants from Yelp Fusion matching the coordinate radius
    and maps them to the local Restaurant Pydantic schema.
    """
    if not settings.YELP_API_KEY:
        return []
    
    url = "https://api.yelp.com/v3/businesses/search"
    headers = {"Authorization": f"Bearer {settings.YELP_API_KEY}"}

    # Convert miles to meters (Yelp radius in is meters; max 40,000m)
    radius_meters = min(int(max_dist_miles * 1609.34), 40000)

    params = {
        "latitude": lat,
        "longitude": lon,
        "radius": radius_meters,
        "categories": "restaurants",
        "limit": 20,
        "sort_by": "distance"
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url, headers=headers, params=params)
            if response.status_code != 200:
                print(f"Yelp API Error: {response.status_code} - {response.text}")
                return []
            
            data = response.json()
            restaurants = []

            for biz in data.get("businesses", []):
                # Map categories to lowercase tags for filtering
                categories = [cat.get("alias", "").lower() for cat in biz.get("categories", [])]

                # Parse pricing level (Yelp return '$', '$$', '$$$', mapping to length 1-4)
                price_str = biz.get("price", "$")
                price_level = min(len(price_str), 4)

                # Convert distance from meters to miles
                dist_meters = biz.get("distance", 0.0)
                distance_miles = round(dist_meters / 1609.34, 1)

                # Join address lines
                address_lines = biz.get("location", {}).get("display_address", [])
                address = ", ".join(address_lines) if address_lines else "Unknown Address"

                restaurants.append(
                    Restaurant(
                        id=biz.get("id", ""),
                        name=biz.get("name", "Unknown Restaurant"),
                        cuisine=biz.get("categories", [{}])[0].get("title", "Other") if biz.get("categories") else "Other",
                        disliked_tags=categories,
                        latitude=biz.get("coordinates", {}).get("latitude", 0.0),
                        longitude=biz.get("coordinates", {}).get("longitude", 0.0),
                        rating=biz.get("rating", 0.0),
                        price_level=price_level,
                        address=address,
                        url=biz.get("url", ""),
                        distance=distance_miles,
                        hours_today="Unknown"
                    )
                )
            return restaurants
    except Exception as e:
        print(f"Failed to connect to Yelp: {str(e)}")
        return []
    
def fetch_restaurant_hours(business_id: str) -> str:
    """
    Queries Yelp Business Details API to fetch and format regular hours for the current day.
    """
    if not settings.YELP_API_KEY:
        return "Unknown"
    
    url = f"https://api.yelp.com/v3/businesses/{business_id}"
    headers = {"Authorization": f"Bearer {settings.YELP_API_KEY}"}

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url, headers=headers)
            if response.status_code != 200:
                return "Unknown"
            
            data = response.json()
            hours_data = data.get("hours", [])
            if not hours_data:
                return "Contact restaurant for hours"
            
            # Yelp date mapping: 0 = Monday, ..., 6 = Sunday
            current_day_idx = datetime.now().weekday()

            # Find active hours for today
            open_periods = hours_data[0].get("open", [])
            today_periods = [p for p in open_periods if p.get("day") == current_day_idx]

            if not today_periods:
                return "Closed today"
            
            # Format opening periods (ex: 11:00 AM - 9:00 PM)
            formatted_periods = []
            for p in today_periods:
                start = format_time(p.get("start", ""))
                end = format_time(p.get("end", ""))
                formatted_periods.append(f"{start} - {end}")

            return ", ".join(formatted_periods)

    except Exception:
        return "Unknown"