# Implementation Plan - "WeEat" Family Meal Planner Agent (TDD Edition)

We are building a sleek, mobile-friendly web application to help families decide where to eat. The app is named **WeEat**.

Workspace Directory: `C:\Users\Ryan\Documents\GitHub\we-eat`

Key Features:
1. **Google Authentication**: Users can log in using their Google account via Firebase Auth.
2. **Family Profile Management**: Create family members and maintain a list of their disliked foods/cuisines.
3. **Active Diner Toggle**: Choose who is eating for a particular meal. The system dynamically computes the combined veto list.
4. **Location-based Search**: Filter restaurants by distance (e.g., within 10 miles or 15 minutes) centered around **Streamwood, IL** (coordinates: `42.0234, -88.1837`) for mock data.
5. **Hybrid Interface**: A sidebar/dashboard to manage profiles/toggles, and a conversational chat interface with an AI Agent (LangChain + OpenAI) to discuss options, suggest places, and respect preferences.

---

## Test-Driven Development (TDD) Strategy

To adhere to the TDD approach, we will write our tests first for each component/feature before writing the functional code.

### Phase 1: Backend TDD
1. **Filter Logic Test**:
   - File: `backend/tests/test_filtering.py`
   - Test cases:
     - Verify restaurants are filtered correctly by distance from Streamwood, IL.
     - Verify active diners' veto lists are unioned and exclude matching cuisines/tags.
     - Verify that if no diners are active, or if no dislikes match, the full list is returned.
2. **Auth Middleware Test**:
   - File: `backend/tests/test_auth.py`
   - Test cases:
     - Verify request is rejected (401) if no Authorization header is present.
     - Verify request is accepted (200) if a valid token is provided.
3. **Recommendation Agent Test**:
   - File: `backend/tests/test_agent.py`
   - Test cases:
     - Mock LangChain agent response and verify integration schema matches.

### Phase 2: Frontend TDD
1. **Diner Selector Component Test**:
   - File: `frontend/src/components/__tests__/DinerSelector.test.tsx`
   - Test cases:
     - Render active diners list.
     - Toggle diner checkbox and verify that the trigger callback fires with updated list.
2. **Profile Manager Component Test**:
   - File: `frontend/src/components/__tests__/ProfileManager.test.tsx`
   - Test cases:
     - Render family members.
     - Fill form to add member with dislikes, click save, verify save handler is called.

---

## User Review Required

> [!IMPORTANT]
> **Firebase & Supabase Setup**
> - **Firebase Auth**: We will configure Firebase Client SDK in the frontend. You will need to create a Firebase project, enable Google Sign-In, and add the config to a `.env` file.
> - **Backend Token Verification**: The FastAPI backend will check the incoming `Authorization: Bearer <token>` header. For local dev without a Firebase Admin SDK key, we will implement a transparent fallback that parses the token's payload directly or uses a dev-mode bypass, ensuring smooth offline building.
> - **Supabase Database**: Since you will build the database out as we go, we will start with a local SQLite/mock database layer that matches the database schema, making it extremely easy to transition to Supabase PostgreSQL later by changing the DB URL.

---

## Proposed Changes

We will create a root project folder at `C:\Users\Ryan\Documents\GitHub\we-eat` with two subdirectories: `frontend` and `backend`.

```mermaid
graph TD
    subgraph Frontend (React 18 + TS)
        Login[Login Page / Firebase Auth] --> App[App Dashboard]
        App --> ProfileMgr[Profile Manager]
        App --> DinerToggle[Active Diners Selector]
        App --> ChatWindow[Chat Agent UI]
        App --> RestaurantList[Filtered Restaurant View]
    end

    subgraph Backend (FastAPI + LangChain)
        API[FastAPI Router] --> AuthMiddleware[Auth & Token Verification]
        AuthMiddleware --> FilterEngine[Logical Filter Engine]
        API --> LangChainAgent[LangChain Agent]
        LangChainAgent --> OpenAI[OpenAI API / Mock LLM]
        API --> DB[SQLite Local / Supabase Postgres]
    end

    App -->|HTTP API / WebSockets| API
```

### Backend (FastAPI + Python)

We will set up a FastAPI backend with the following structure:
- **`backend/app/main.py`**: Entry point, CORS, and auth middleware.
- **`backend/app/config.py`**: Configuration management using `pydantic-settings`.
- **`backend/app/database.py`**: Database connection layer (SQLite/PostgreSQL switcher).
- **`backend/app/schemas.py`**: Pydantic schemas for request validation.
- **`backend/app/auth.py`**: Firebase ID token verification logic.
- **`backend/app/agent.py`**: LangChain agent setup with prompt templates for restaurant recommendations.
- **`backend/app/mock_data.py`**: A curated list of mock restaurants around **Streamwood, IL** (e.g. Elgin, Schaumburg, Hoffman Estates) with coordinates and tags.

#### Database Schema
1. `family_members`
   - `id` (UUID or Serial, PK)
   - `user_id` (Text, Firebase UID of the logged-in user to keep profiles private)
   - `name` (Text)
   - `dislikes` (Text[], array of disliked foods/cuisines/ingredients)
2. `restaurants`
   - `id` (UUID or Serial, PK)
   - `name` (Text)
   - `cuisine` (Text)
   - `disliked_tags` (Text[], e.g., `["pizza", "italian"]`)
   - `latitude` (Float)
   - `longitude` (Float)
   - `rating` (Float)
   - `price_level` (Int, 1-4)
   - `address` (Text)

---

### Frontend (React 18 + TS + Vite)

We will initialize the frontend using Vite:
- **`frontend/src/firebase.ts`**: Firebase App initialization and Google Auth provider setup.
- **`frontend/src/App.tsx`**: State coordinator (Auth guard, loading states).
- **`frontend/src/components/Login.tsx`**: Sleek, glassmorphic sign-in page with a "Sign in with Google" button.
- **`frontend/src/components/ChatAgent.tsx`**: Interactive chat interface with message bubbles and typing states.
- **`frontend/src/components/ProfileManager.tsx`**: Add, edit, and delete family members and their veto list.
- **`frontend/src/components/DinerSelector.tsx`**: Quick checkboxes to toggle who is eating.
- **`frontend/src/components/RestaurantCard.tsx`**: Premium visual cards for restaurants showing distance, match status, and details.
- **`frontend/src/index.css`**: CSS Design System containing custom fonts, dark-mode styling, glassmorphism UI variables, and micro-animations.

---

## Verification Plan

### Automated Tests
- `pytest backend/tests/test_filtering.py`: Verifies that if member "Olivia" dislikes "pizza", pizza restaurants are excluded when she is checked, and included when she is unchecked.
- Verify Firebase authentication header parsing in backend.

### Manual Verification
1. Run the FastAPI server and Vite dev server.
2. Log in using Google (or via Firebase emulator / mock user if configuration is skipped).
3. Create family profiles (e.g. Olivia dislikes Pizza).
4. Verify distance-based calculations match the Streamwood, IL area coordinates (e.g., restaurants in Schaumburg show up as ~6-8 miles away, whereas Elgin shows up as ~5-7 miles away).
5. Verify the chat agent responds with Streamwood-local restaurant suggestions that respect diner vetos.
