# Food Verse AI — Multimodal Food Intelligence Agent

A modular full-stack MVP for food recognition, nutrition estimation, freshness screening, kitchen hygiene review, cooking assistance, and personalized meal planning.

## Stack
- Frontend: React + Vite + TypeScript + Tailwind CSS + Recharts
- Backend: Python 3.10+ + FastAPI + Pydantic
- AI provider: Gemini API (optional; deterministic demo fallbacks are included)
- Persistence: local JSON history in the backend for the starter build

> Important: model outputs are estimates, not laboratory food-safety tests or medical advice. Image-based freshness/hygiene checks cannot certify food as safe.

## Run locally

### 1. Backend
```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```
Open http://localhost:8000/docs

### 2. Frontend
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```
Open the URL printed by Vite (usually http://localhost:5173).

## Configure Gemini (optional)
Set `GEMINI_API_KEY` in `backend/.env`. The app works in demo mode without it. The API key must stay on the backend and must never be placed in the frontend.

## Modules
1. Food recognition + nutrition estimate
2. Freshness screening
3. Restaurant/kitchen hygiene review
4. Smart cooking assistant
5. Personalized meal planner

## Project workflow / epics
- Epic 1: requirements and environment setup
- Epic 2: food recognition and nutrition
- Epic 3: freshness screening
- Epic 4: kitchen hygiene analysis
- Epic 5: cooking assistant and meal planner
- Epic 6: UI, testing and deployment

## Limitations and responsible use
- Demo fallback results are illustrative, not real model predictions.
- Vision checks identify visible indicators only; they cannot detect pathogens, toxins, internal spoilage, or hidden contamination.
- Nutrition values vary by recipe, portion size, and preparation method.
- For allergies, medical diets, or food-safety decisions, verify with authoritative sources and qualified professionals.

## GitHub
```bash
git init
git add .
git commit -m "Build Food Verse AI MVP"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/food-verse-ai.git
git push -u origin main
```
