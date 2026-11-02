from pydantic import BaseModel, Field
from typing import Any

class FoodTextRequest(BaseModel):
    prompt: str = Field(min_length=2, max_length=3000)
    dietary_preference: str = "Vegetarian"
    calorie_target: int = Field(default=2000, ge=800, le=6000)
    servings: int = Field(default=2, ge=1, le=12)

class MealPlanRequest(BaseModel):
    goal: str = "Balanced"
    dietary_preference: str = "Vegetarian"
    calorie_target: int = Field(default=2000, ge=800, le=6000)
    meals_per_day: int = Field(default=3, ge=2, le=6)
    avoid: str = ""

class AnalysisResponse(BaseModel):
    module: str
    title: str
    summary: str
    findings: list[str]
    recommendations: list[str]
    confidence: str = "Demo estimate"
    disclaimer: str
    data: dict[str, Any] = {}
