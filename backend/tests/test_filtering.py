import pytest
from app.schemas import Diner, Restaurant
from app.filter import filter_restaurants

# Mock Restaurant Data centered around Streamwood, IL (coordinates: 42.0234, -88.1837)
MOCK_RESTAURANTS = [
    Restaurant(
        id="1",
        name="Streamwood Pizza Co",
        cuisine="Pizza",
        disliked_tags=["pizza", "italian", "cheese"],
        latitude=42.0234,  # Streamwood center point
        longitude=-88.1837,
        rating=4.5,
        price_level=2,
        address="123 Main St, Streamwood, IL",
        url="streamwoodpizzaco.com",
        distance=2.0,
        hours_today="12:00 PM - 10:00 PM"
    ),
    Restaurant(
        id="2",
        name="Elgin Burger Joint",
        cuisine="Burgers",
        disliked_tags=["burger", "beef", "fast-food"],
        latitude=42.0350,  # ~5 miles from Streamwood center
        longitude=-88.2830,
        rating=4.2,
        price_level=1,
        address="456 State St, Elgin, IL",
        url="elginburgerjoint.com",
        distance=3.0,
        hours_today="11:00 AM - 9:00 PM"
    ),
    Restaurant(
        id="3",
        name="Schaumburg Sushi",
        cuisine="Sushi",
        disliked_tags=["sushi", "fish", "raw"],
        latitude=42.0270,  # ~7.5 miles from Streamwood center
        longitude=-88.0830,
        rating=4.8,
        price_level=3,
        address="789 Golf Rd, Schaumburg, IL",
        url="schaumburgsushi.com",
        distance=5.0,
        hours_today="10:00 AM - 10:00 PM"
    ),
    Restaurant(
        id="4",
        name="Hoffman Estates Tacos",
        cuisine="Mexican",
        disliked_tags=["tacos", "mexican", "spicy"],
        latitude=42.0630,  # ~6 miles from Streamwood center
        longitude=-88.1330,
        rating=4.4,
        price_level=2,
        address="321 Higgins Rd, Hoffman Estates, IL",
        url="hoffmanestate.com",
        distance=3.5,
        hours_today="1:00 PM - 11:00 PM"
    )
]

# Center coordinates for our searches (Streamwood, IL)
STREAMWOOD_LAT = 42.0234
STREAMWOOD_LON = -88.1837

def test_no_filters_returns_all():
    """If no active diners and max distance is large, all restaurants should be returned."""
    diners = []
    filtered = filter_restaurants(
        restaurants=MOCK_RESTAURANTS,
        diners=diners,
        user_lat=STREAMWOOD_LAT,
        user_lon=STREAMWOOD_LON,
        max_distance_miles=15.0
    )
    assert len(filtered) == 4

def test_distance_filtering():
    """Verify that restaurants outside the max distance are excluded."""
    # Elgin Burger Joint is ~5.1 miles away
    # Schaumburg Sushi is ~5.1 miles away
    # Hoffman Estates Tacos is ~4.1 miles away
    # Streamwood Pizza Co is 0 miles away
    
    # If we filter within 2 miles, only Streamwood Pizza Co should return
    filtered = filter_restaurants(
        restaurants=MOCK_RESTAURANTS,
        diners=[],
        user_lat=STREAMWOOD_LAT,
        user_lon=STREAMWOOD_LON,
        max_distance_miles=2.0
    )
    assert len(filtered) == 1
    assert filtered[0].name == "Streamwood Pizza Co"

def test_single_diner_veto():
    """If a diner dislikes pizza and is active, pizza restaurants should be filtered out."""
    diners = [
        Diner(name="Olivia", is_active=True, dislikes=["pizza", "sushi"])
    ]
    filtered = filter_restaurants(
        restaurants=MOCK_RESTAURANTS,
        diners=diners,
        user_lat=STREAMWOOD_LAT,
        user_lon=STREAMWOOD_LON,
        max_distance_miles=15.0
    )
    # Streamwood Pizza (pizza) and Schaumburg Sushi (sushi) should be excluded
    assert len(filtered) == 2
    remaining_names = [r.name for r in filtered]
    assert "Elgin Burger Joint" in remaining_names
    assert "Hoffman Estates Tacos" in remaining_names
    assert "Streamwood Pizza Co" not in remaining_names
    assert "Schaumburg Sushi" not in remaining_names

def test_diner_veto_ignored_when_inactive():
    """If a diner dislikes pizza but is NOT eating, pizza restaurants should NOT be filtered out."""
    diners = [
        Diner(name="Olivia", is_active=False, dislikes=["pizza"])
    ]
    filtered = filter_restaurants(
        restaurants=MOCK_RESTAURANTS,
        diners=diners,
        user_lat=STREAMWOOD_LAT,
        user_lon=STREAMWOOD_LON,
        max_distance_miles=15.0
    )
    assert len(filtered) == 4

def test_multiple_diners_union_vetoes():
    """If multiple active diners are eating, their veto lists should combine."""
    diners = [
        Diner(name="Olivia", is_active=True, dislikes=["pizza"]),
        Diner(name="Peyton", is_active=True, dislikes=["mexican"])
    ]
    filtered = filter_restaurants(
        restaurants=MOCK_RESTAURANTS,
        diners=diners,
        user_lat=STREAMWOOD_LAT,
        user_lon=STREAMWOOD_LON,
        max_distance_miles=15.0
    )
    # Streamwood Pizza (pizza) and Hoffman Estates Tacos (mexican) should be excluded
    assert len(filtered) == 2
    remaining_names = [r.name for r in filtered]
    assert "Elgin Burger Joint" in remaining_names
    assert "Schaumburg Sushi" in remaining_names