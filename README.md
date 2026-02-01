# Faceless Video Generator

A professional "Pictory/InVideo"-style web application for creating faceless videos with AI voiceovers, stock footage, and dynamic subtitles.

## 🚀 Quick Start

### 1. Start the Backend (Server)
Open a terminal and run:
```bash
source venv/bin/activate
cd server
uvicorn main:app --reload --port 8000
```

### 2. Start the Frontend (Client)
Open a new terminal and run:
```bash
cd client
npm run dev
```
Access the app at: **http://localhost:5173** (or 5174/5175 if port is busy)

---

## 📖 User Guide

### 1. Create a Story
You have two options to create your video script:
*   **AI Write:** Click the **"AI Write"** button (Magic Wand) at the top right. Enter a topic (e.g., "The History of Rome") and hit Generate. The AI will create a sequence of scenes for you.
*   **Manual:** Click **"Add New Scene"** at the bottom to add blocks manually. Type your script into the text area for each block.

### 2. Add Visuals
For each scene, choose a visual background:
*   **Gameplay:** Click the "Gameplay" button to loop a default background (e.g., Minecraft, Subway Surfers).
*   **Pexels:** Click the Image icon to open the **Stock Footage Search**. Type a keyword (e.g., "Ocean", "City") and select a video. The app will download and apply it during rendering.

### 3. Customize Style
Use the **Sidebar** to customize the look and sound:
*   **Voice Lab:** Choose an AI narrator (e.g., Christopher, Aria).
*   **Style Studio:** Change subtitle font, color, position, and stroke.
*   **Music:** Adjust background music volume.

### 4. Render Video
1.  Look at the **Preview Player** on the right.
2.  Click the **"Generate Video"** button.
3.  Wait for the backend to process (TTS generation, video downloading, composting).
4.  Once done, the video will play automatically. You can download it using the **"Download MP4"** link.

---

## 🛠 Tech Stack
*   **Frontend:** React, Vite, Tailwind CSS, Zustand, Framer Motion
*   **Backend:** Python FastAPI, MoviePy v2.0
*   **AI Services:** OpenAI (Script), Edge-TTS (Voice), Whisper (Subtitles), Pexels API (Stock Video)
