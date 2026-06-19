# Phase 1 Guide: Project Setup & First TDD Test

This guide walks you through setting up the environment for **WeEat** and writing the first test suite for our restaurant filtering logic.

---

## Step 1: Directory Setup
Open your terminal (PowerShell in VS Code) at `C:\Users\Ryan\Documents\GitHub\we-eat` and run the following commands to create the initial folder structure:

```powershell
# Create backend and frontend directories
mkdir backend
mkdir frontend

# Inside backend, create the app and tests folders
mkdir backend/app
mkdir backend/tests
```

---

## Step 2: Backend Dependencies & Environment Setup
Create a file named `requirements.txt` inside the `backend` folder:

### [NEW] `backend/requirements.txt`
```text
fastapi==0.111.0
uvicorn==0.30.1
pydantic==2.7.4
pydantic-settings==2.3.3
pytest==8.2.2
openai==1.34.0
langchain==0.2.5
langchain-openai==0.1.9
supabase==2.5.1
httpx==0.27.0
```

Now run the following commands in your terminal to set up the Python virtual environment and install the dependencies:

```powershell
# Navigate to the backend directory
cd backend

# Create a virtual environment named 'venv'
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\Activate.ps1

# Upgrade pip and install the dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## Step 3: Backend Configuration Files
Create the environment configuration files inside the `backend` folder to manage secrets (like OpenAI and Supabase credentials).

### [NEW] `backend/.env.example`
```env
# Server Configuration
PORT=8000
HOST=127.0.0.1
ENVIRONMENT=development

# Database Configuration (Supabase or local SQLite fallback)
DATABASE_URL=sqlite:///./we_eat.db
SUPABASE_URL=your-supabase-project-url
SUPABASE_KEY=your-supabase-anon-key

# AI Configuration
OPENAI_API_KEY=your-openai-api-key

# Firebase Configuration
FIREBASE_PROJECT_ID=your-firebase-project-id
```

### [NEW] `backend/.env`
For now, you can copy the example file to `.env`. (Fill in your actual OpenAI and Supabase credentials when you are ready, or leave them as placeholders since we'll write fallbacks).
```powershell
cp .env.example .env
```

---

## Step 4: Write the First TDD Test
We will write the tests for the restaurant filtering logic before we write any of the filtering code. This ensures our implementation matches the exact requirements.

Create a file named `test_filtering.py` inside the `backend/tests` folder:

### [NEW] `backend/tests/test_filtering.py`
```python
import pytest
from app.schemas import Diner, Restaurant
from app.filter import filter_restaurants

# Mock Restaurant Data for testing
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
        latitude=42.0350,  # ~5 miles from Streamwood center
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
        latitude=42.0270,  # ~7.5 miles from Streamwood center
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
        latitude=42.0630,  # ~6 miles from Streamwood center
        longitude=-88.1330,
        rating=4.4,
        price_level=2,
        address="321 Higgins Rd, Hoffman Estates, IL"
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
```

---

## Step 5: Run the Failing Test
After you have created the files and set up your virtual environment, run the test runner in your backend terminal:

```powershell
python -m pytest
```

It should fail immediately with an `ImportError` because `app.schemas` and `app.filter` do not exist yet. This is exactly what we want in TDD!

Let me know once you have created these files and run the test!
