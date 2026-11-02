from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from io import BytesIO
from datetime import datetime, timezone
import json
from pathlib import Path
from .config import settings
from .schemas import FoodTextRequest, MealPlanRequest
from .ai import ask_gemini

app = FastAPI(title=settings.app_name, version="1.0.0", description="Multimodal food intelligence API")
app.add_middleware(CORSMiddleware, allow_origins=[settings.frontend_origin, "http://127.0.0.1:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
HISTORY = Path(__file__).parent / "history.json"

def save_history(module: str, title: str, summary: str):
    try:
        items = json.loads(HISTORY.read_text()) if HISTORY.exists() else []
        items.insert(0, {"id": datetime.now(timezone.utc).isoformat(), "module": module, "title": title, "summary": summary})
        HISTORY.write_text(json.dumps(items[:30], indent=2))
    except Exception:
        pass

def demo(title, summary, findings, recommendations, data=None):
    return {"title": title, "summary": summary, "findings": findings, "recommendations": recommendations, "confidence": "Illustrative demo result", "data": data or {}}

@app.get("/")
async def root():
    return {"name": settings.app_name, "status": "running", "docs": "/docs"}

@app.get("/api/health")
async def health():
    return {"status": "ok", "ai_configured": bool(settings.gemini_api_key)}

@app.get("/api/history")
async def history():
    return json.loads(HISTORY.read_text()) if HISTORY.exists() else []

async def validate_image(file: UploadFile):
    content = await file.read()
    if len(content) > 8 * 1024 * 1024:
        raise HTTPException(413, "Image must be 8 MB or smaller.")
    try:
        image = Image.open(BytesIO(content))
        image.verify()
    except Exception:
        raise HTTPException(400, "Please upload a valid image file.")
    if image.format not in ("JPEG", "PNG", "WEBP"):
        raise HTTPException(400, "Supported formats: JPG, PNG, WEBP.")
    return content, f"image/{image.format.lower() if image.format != 'JPEG' else 'jpeg'}"

@app.post("/api/food/recognize")
async def recognize(file: UploadFile = File(...)):
    content, mime = await validate_image(file)
    result = await ask_gemini("Identify visible food items. Estimate a plausible serving and nutrition range. Avoid false precision. Return the required JSON. Include data with calories, protein_g, carbs_g, fat_g, detected_items.", content, mime)
    if not result:
        result = demo("Food image analyzed", "Demo mode: image upload and validation worked. Configure GEMINI_API_KEY for AI-based identification.", ["Image received and validated", "No real model inference was performed in demo mode"], ["Add a clear, well-lit top-down photo", "Verify portion size and ingredients before relying on nutrition values"], {"calories": 420, "protein_g": 18, "carbs_g": 54, "fat_g": 14, "detected_items": ["Example grain bowl"]})
    save_history("Food recognition", result["title"], result["summary"])
    return {"module": "recognition", "disclaimer": "Nutrition is an estimate and varies with ingredients and portion size.", **result}

@app.post("/api/food/freshness")
async def freshness(file: UploadFile = File(...)):
    content, mime = await validate_image(file)
    result = await ask_gemini("Review this produce/food image for visible freshness indicators only. Describe visible discoloration, bruising, mold-like appearance or texture if apparent. Do not certify safety or infer pathogens. Return JSON.", content, mime)
    if not result:
        result = demo("Freshness visual screening", "Demo mode: upload received. Configure Gemini for image-based visual screening.", ["Visible appearance can be reviewed, but image-only checks are limited", "Odor, storage temperature, expiry and internal condition are unknown"], ["Check smell, texture, date and storage history", "When in doubt, discard; do not taste questionable food"], {"visual_status": "Needs human inspection"})
    save_history("Freshness", result["title"], result["summary"])
    return {"module": "freshness", "disclaimer": "A photo cannot establish food safety or detect pathogens, toxins, or internal spoilage.", **result}

@app.post("/api/kitchen/hygiene")
async def hygiene(file: UploadFile = File(...)):
    content, mime = await validate_image(file)
    result = await ask_gemini("Review this kitchen/food-service image for visible hygiene risk indicators only (e.g. uncovered food, visible clutter, cross-contamination cues, handwashing access if visible). Do not certify compliance. Return JSON.", content, mime)
    if not result:
        result = demo("Kitchen hygiene visual review", "Demo mode: upload received. Configure Gemini for visual review.", ["Image-only review cannot verify cleaning records, temperatures, staff practices or microbiological safety"], ["Keep raw and ready-to-eat foods separate", "Use covered, labeled storage", "Verify cleaning schedules and food temperatures with records"], {"risk_level": "Not assessed"})
    save_history("Kitchen hygiene", result["title"], result["summary"])
    return {"module": "hygiene", "disclaimer": "This is not a regulatory inspection or food-safety certification.", **result}

@app.post("/api/cooking/assistant")
async def cooking(req: FoodTextRequest):
    prompt = f"Create practical cooking guidance for: {req.prompt}. Dietary preference: {req.dietary_preference}. Servings: {req.servings}. Return JSON with ingredients, steps, prep_minutes, cook_minutes in data."
    result = await ask_gemini(prompt)
    if not result:
        result = demo("Smart cooking suggestion", f"Demo recipe guidance for {req.prompt}.", ["Demo recipe is a starting point; adjust based on available ingredients"], ["Prepare ingredients first", "Cook thoroughly and avoid cross-contamination", "Taste and adjust seasoning"], {"ingredients": ["Main ingredient from your prompt", "Onion", "Tomato", "Spices", "Cooking oil"], "steps": ["Wash and prepare ingredients.", "Cook aromatics and spices.", "Add the main ingredient and cook until done.", "Serve hot."], "prep_minutes": 10, "cook_minutes": 20})
    save_history("Cooking assistant", result["title"], result["summary"])
    return {"module": "cooking", "disclaimer": "Follow safe handling and cooking temperatures appropriate to the ingredients.", **result}

@app.post("/api/nutrition/meal-plan")
async def meal_plan(req: MealPlanRequest):
    prompt = f"Create a one-day meal plan. Goal: {req.goal}; diet: {req.dietary_preference}; calorie target: {req.calorie_target}; meals/day: {req.meals_per_day}; avoid: {req.avoid or 'nothing specified'}. Return JSON with data.meals array; each meal has name, time, calories, protein_g, description. Keep nutrition estimates approximate."
    result = await ask_gemini(prompt)
    if not result:
        meals = [
            {"name":"Breakfast · Oats & milk","time":"8:00 AM","calories":400,"protein_g":16,"description":"Oats, milk, banana and nuts"},
            {"name":"Lunch · Dal, rice & curd","time":"1:00 PM","calories":620,"protein_g":24,"description":"Dal, rice, seasonal vegetables and curd"},
            {"name":"Snack · Roasted chana","time":"5:00 PM","calories":220,"protein_g":11,"description":"Roasted chana with fruit"},
            {"name":"Dinner · Paneer roti plate","time":"8:30 PM","calories":600,"protein_g":32,"description":"Paneer bhurji, whole-wheat rotis and salad"}
        ]
        result = demo("Your balanced day", "A sample vegetarian plan. Adjust portions to your appetite, activity and actual nutrition needs.", ["Approximate daily energy: 1,840 kcal", "Approximate protein: 83 g"], ["Track actual portions for better estimates", "Change foods to match allergies, budget and availability"], {"meals": meals, "total_calories": 1840, "total_protein_g": 83})
    save_history("Meal planner", result["title"], result["summary"])
    return {"module": "meal-plan", "disclaimer": "General wellness information, not a medical diet. Consult a qualified professional for medical nutrition needs.", **result}
