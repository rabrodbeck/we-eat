# WeEat - Implementation Task List

This task list tracks the step-by-step TDD implementation of the **WeEat** application.

## [x] Phase 1: Environment & Setup
- `[x]` Initialize project directories at `C:\Users\Ryan\Documents\GitHub\we-eat` (`/backend` and `/frontend`)
- `[x]` Set up backend virtual environment and install packages (`fastapi`, `uvicorn`, `pytest`, `pydantic`, `langchain`, `openai`, `supabase`)
- `[x]` Create environment files (`.env` and `.env.example` in both frontend and backend)

## [x] Phase 2: Backend Test-Driven Development (TDD)
- `[x]` **Task 2.1: Filter Logic**
  - `[x]` Write `backend/tests/test_filtering.py` (verifying distance math and member veto checks)
  - `[x]` Verify test fails (`pytest`)
  - `[x]` Implement `backend/app/mock_data.py` (restaurants around Streamwood, IL)
  - `[x]` Implement filtering logic in `backend/app/filter.py`
  - `[x]` Verify test passes (`pytest`)
- `[x]` **Task 2.2: Auth Middleware**
  - `[x]` Write `backend/tests/test_auth.py` (verifying token verification rejects unauthenticated requests)
  - `[x]` Verify test fails (`pytest`)
  - `[x]` Implement Firebase token verification middleware in `backend/app/auth.py`
  - `[x]` Verify test passes (`pytest`)
- `[x]` **Task 2.3: LangChain & OpenAI Agent**
  - `[x]` Write `backend/tests/test_agent.py` (verifying prompt context and OpenAI interaction)
  - `[x]` Verify test fails (`pytest`)
  - `[x]` Implement LangChain agent and endpoint in `backend/app/agent.py` and `backend/app/main.py`
  - `[x]` Verify test passes (`pytest`)

## [x] Phase 3: Frontend Test-Driven Development (TDD)
- `[x]` **Task 3.1: Frontend Setup**
  - `[x]` Scaffold React 18 + TS + Vite in `frontend`
  - `[x]` Install packages (`firebase`, `vitest`, `@testing-library/react`, `@testing-library/jest-dom`)
- `[x]` **Task 3.2: Diner Selector Component**
  - `[x]` Write `frontend/src/components/__tests__/DinerSelector.test.tsx`
  - `[x]` Verify test fails (`npm run test`)
  - `[x]` Implement `DinerSelector.tsx`
  - `[x]` Verify test passes
- `[x]` **Task 3.3: Profile Manager Component**
  - `[x]` Write `frontend/src/components/__tests__/ProfileManager.test.tsx`
  - `[x]` Verify test fails
  - `[x]` Implement `ProfileManager.tsx`
  - `[x]` Verify test passes
- `[x]` **Task 3.4: Authentication & Login Page**
  - `[x]` Write `frontend/src/components/__tests__/Login.test.tsx`
  - `[x]` Verify test fails
  - `[x]` Set up `firebase.ts` and implement `Login.tsx` with Google Auth
  - `[x]` Verify test passes

## [/] Phase 4: Integration, Styling, and Polish
- `[x]` Implement premium design system in `frontend/src/index.css` (Glassmorphism, dark/light toggle, micro-animations)
- `[x]` Connect React app to FastAPI endpoints
- `[x]` Deploy frontend to Vercel (resolving Firebase authorized domains) and backend to Hugging Face Spaces (with Docker)


