import requests
import json
import sys
import os

# Define the endpoint
url = "http://localhost:8000/render"

# Define the payload with Viral Shorts features
payload = {
    "global_settings": {
        "voice": "en-US-ChristopherNeural",
        "music_vol": 0.1
    },
    "scenes": [
        {
            "text": "This is the new viral engine test.",
            "media_type": "gameplay",
            "media_url": None, # Will use default Minecraft background
            "transition": "glitch",
            "effect": "zoom_slam"
        },
        {
            "text": "Notice the pop animations and safe zones.",
            "media_type": "gameplay",
            "media_url": None,
            "transition": "whip_pan",
            "effect": "rgb_split"
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

headers = {
    "Content-Type": "application/json"
}

print(f"🎬 Sending render request to {url}...")
print("Payload summary:")
print(f" - Scenes: {len(payload['scenes'])}")
print(f" - Effects: {payload['scenes'][0]['effect']}, {payload['scenes'][1]['effect']}")
print(f" - Subtitle Pop Intensity: {payload['subtitle_settings']['popIntensity']}")

try:
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        output_filename = "viral_demo.mp4"
        with open(output_filename, "wb") as f:
            f.write(response.content)
        print(f"\n✅ Success! Video saved to: {os.path.abspath(output_filename)}")
        print("You can now open this file to see the results.")
    else:
        print(f"\n❌ Error: Status Code {response.status_code}")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"\n❌ Request failed: {e}")
    print("Ensure the server is running on localhost:8000")
