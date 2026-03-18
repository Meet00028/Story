from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn
import os
import json
import requests
from pydantic import BaseModel
from typing import List, Optional
import engine
from openai import OpenAI

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Config
with open("config.json", "r") as f:
    CONFIG = json.load(f)

PEXELS_API_KEY = CONFIG.get("PEXELS_API_KEY")
OPENAI_API_KEY = CONFIG.get("OPENAI_API_KEY")

openai_client = OpenAI(api_key=OPENAI_API_KEY)

class Scene(BaseModel):
    text: str
    media_type: str = "gameplay"
    media_url: Optional[str] = None
    transition: str = "none"
    effect: str = "none"

class RenderRequest(BaseModel):
    global_settings: dict
    scenes: List[Scene]
    subtitle_settings: dict

@app.get("/api/pexels/search")
async def search_pexels(query: str, per_page: int = 15):
    if not PEXELS_API_KEY:
        raise HTTPException(status_code=500, detail="Pexels API Key not configured")
    
    url = f"https://api.pexels.com/videos/search?query={query}&per_page={per_page}&orientation=portrait"
    headers = {"Authorization": PEXELS_API_KEY}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

class StoryRequest(BaseModel):
    prompt: str

@app.post("/api/story/generate")
async def generate_story(request: StoryRequest):
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API Key not configured")

    prompt = f"""
    Write a short video script about: "{request.prompt}".
    Return ONLY a JSON array of scenes. Each scene object must have:
    - "text": The narration script (1-2 sentences).
    - "media_keyword": A keyword to search for visuals (e.g., "ocean", "city").
    - "transition": "fade" or "none".
    - "effect": "zoom_in" or "none".
    
    Example:
    [
        {{"text": "The ocean is vast and mysterious.", "media_keyword": "ocean waves", "transition": "fade", "effect": "zoom_in"}},
        {{"text": "But what lies beneath?", "media_keyword": "underwater", "transition": "none", "effect": "none"}}
    ]
    """

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        # Handle case where GPT wraps in { "scenes": [...] } or just [...]
        data = json.loads(content)
        if isinstance(data, dict) and "scenes" in data:
            return data["scenes"]
        elif isinstance(data, list):
            return data
        else:
            # Fallback for weird wrapping
            for key in data:
                if isinstance(data[key], list):
                    return data[key]
            return []
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/render")
async def render_video_endpoint(request: RenderRequest):
    try:
        # Convert Pydantic model to dict
        data = request.model_dump()
        output_file = await engine.render_video(data)
        return FileResponse(output_file, media_type="video/mp4", filename="rendered_video.mp4")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
