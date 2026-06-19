from app.schemas import Restaurant

# Coordinates centered around Streamwood, IL: 42.0234, -88.1837
MOCK_RESTAURANTS = [
    Restaurant(
        id=1,
        name="Streamwood Pizza Co",
        cuisine="Pizza",
        disliked_tags=["pizza", "italian", "cheese"],
        latitude=42.0234,  # Streamwood center point
        longitude=-88.1837,
        rating=4.5,
        price_level=2,
        address="123 Main St, Streamwood, IL"
    ),
    Restaurant(
        id=2,
        name="Elgin Burger Joint",
        cuisine="Burgers",
        disliked_tags=["burger", "beef", "fast-food"],
        latitude=42.0350,  # ~5.1 miles from Streamwood center
        longitude=-88.2830,
        rating=4.2,
        price_level=1,
        address="456 State St, Elgin, IL"
    ),
    Restaurant(
        id=3,
        name="Schaumburg Sushi",
        cuisine="Sushi",
        disliked_tags=["sushi", "fish", "raw"],
        latitude=42.0270,  # ~5.1 miles from Streamwood center
        longitude=-88.0830,
        rating=4.8,
        price_level=3,
        address="789 Golf Rd, Schaumburg, IL"
    ),
    Restaurant(
        id=4,
        name="Hoffman Estates Tacos",
        cuisine="Mexican",
        disliked_tags=["tacos", "mexican", "spicy"],
        latitude=42.0630,  # ~4.1 miles from Streamwood center
        longitude=-88.1330,
        rating=4.4,
        price_level=2,
        address="321 Higgins Rd, Hoffman Estates, IL"
    )
]