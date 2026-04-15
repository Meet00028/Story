
import sys
import os
import json
import asyncio
from engine import render_video

# Define the payload with Viral Shorts features
payload = {
    "global_settings": {
        "voice": "en-US-ChristopherNeural",
        "music_vol": 0.1
    },
    "scenes": [
        {
            "text": "Goofy pythons jumping joyfully.",
            "media_type": "gameplay",
            "media_url": None, # Will use default Minecraft background
            "transition": "glitch",
            "effect": "zoom_slam"
        }
    ],
    "subtitle_settings": {
        "font": "Arial",
        "color": "#ffffff",
        "strokeColor": "#000000",
        "position": "center",
        "highlightStyle": "nouns",
        "popIntensity": 1.2
    }
}

print("🎬 Starting Direct Render Verification...")
try:
    output_file = asyncio.run(render_video(payload))
    print(f"✅ Render successful! Output saved to: {output_file}")
except Exception as e:
    print(f"❌ Render failed: {e}")
    import traceback
    traceback.print_exc()
