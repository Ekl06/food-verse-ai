import base64, json
import httpx
from .config import settings

SYSTEM = (
    "You are Food Verse AI, a cautious food intelligence assistant. "
    "Return valid JSON only with keys title, summary, findings (array), "
    "recommendations (array), confidence, data (object). "
    "Never claim an image proves food is safe, detects pathogens, or certifies hygiene. "
    "State uncertainty and recommend human verification for safety-critical decisions."
)

async def ask_gemini(prompt: str, image_bytes: bytes | None = None, mime_type: str = "image/jpeg"):
    if not settings.gemini_api_key:
        return None
    parts = [{"text": SYSTEM + "\n\n" + prompt}]
    if image_bytes:
        parts.append({"inline_data": {"mime_type": mime_type, "data": base64.b64encode(image_bytes).decode()}})
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.gemini_model}:generateContent?key={settings.gemini_api_key}"
    payload = {"contents": [{"parts": parts}], "generationConfig": {"responseMimeType": "application/json", "temperature": 0.2}}
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        body = response.json()
    text = body["candidates"][0]["content"]["parts"][0]["text"]
    return json.loads(text)
