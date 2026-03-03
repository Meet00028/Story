import os
import json
import asyncio
import requests
import re
import whisper
import edge_tts
from openai import OpenAI
from moviepy import *
import moviepy.video.fx as vfx
import moviepy.audio.fx as afx
# from moviepy.video.compositing.concatenate import concatenate_videoclips
# from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
# from moviepy.audio.AudioClip import CompositeAudioClip
# from moviepy.audio.compositing.concatenate import concatenate_audioclips
# from moviepy.audio.io.AudioFileClip import AudioFileClip
from utils import load_config, create_ken_burns_clip, generate_dynamic_subtitles

# Load Config
CONFIG = load_config()
OPENAI_API_KEY = CONFIG.get("OPENAI_API_KEY")
PEXELS_API_KEY = CONFIG.get("PEXELS_API_KEY")

if not OPENAI_API_KEY:
    print("WARNING: OPENAI_API_KEY not found in config.json")
if not PEXELS_API_KEY:
    print("WARNING: PEXELS_API_KEY not found in config.json")

# Initialize OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

async def generate_script(topic):
    print(f"Generating script for topic: {topic}...")
    prompt = f"""
    You are a viral video director. Create a script for a short video about "{topic}".
    The script must be formatted as a JSON list of "Scenes".
    Each scene must have:
    - "sentence": The voiceover text.
    - "visual_keyword": A search term for stock footage or image generation.
    - "type": Either "ai_image" or "stock_video".
    
    Example format:
    [
        {{"sentence": "Rome fell in a day...", "visual_keyword": "burning roman city", "type": "ai_image"}},
        {{"sentence": "But the army remained...", "visual_keyword": "roman soldiers marching", "type": "stock_video"}}
    ]
    
    Keep it fast-paced. Total 3-5 scenes.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "You are a creative director."},
                  {"role": "user", "content": prompt}],
        response_format={ "type": "json_object" }
    )
    
    content = response.choices[0].message.content
    # Ensure we get the list inside the JSON object if it's wrapped
    try:
        data = json.loads(content)
        if isinstance(data, list):
            return data
        elif "scenes" in data:
            return data["scenes"]
        else:
            # Try to find list in values
            for val in data.values():
                if isinstance(val, list):
                    return val
            return []
    except Exception as e:
        print(f"Error parsing script: {e}")
        return []

async def generate_audio(text, output_file="voiceover.mp3"):
    print("Generating audio...")
    voice = "en-US-ChristopherNeural" # Good male voice
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

def get_word_timestamps(audio_file):
    print("Transcribing audio for timestamps...")
    model = whisper.load_model("base")
    # suppress_silence=True helps with timing
    result = model.transcribe(audio_file, word_timestamps=True)
    
    all_words = []
    for segment in result["segments"]:
        for word in segment["words"]:
            all_words.append({
                "word": word["word"].strip(),
                "start": word["start"],
                "end": word["end"]
            })
    return all_words

def download_file(url, filename):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
    else:
        print(f"Failed to download {url}")

def get_visual_asset(scene, index):
    keyword = scene["visual_keyword"]
    asset_type = scene["type"]
    filename = f"assets/scene_{index}_{asset_type}.mp4" if asset_type == "stock_video" else f"assets/scene_{index}_{asset_type}.png"
    
    if os.path.exists(filename):
        return filename

    print(f"Getting visual for: {keyword} ({asset_type})")
    
    if asset_type == "ai_image":
        try:
            response = client.images.generate(
                model="dall-e-3",
                prompt=f"Cinematic, realistic, 8k image of {keyword}",
                size="1024x1024",
                quality="standard",
                n=1
            )
            image_url = response.data[0].url
            download_file(image_url, filename)
        except Exception as e:
            print(f"DALL-E error: {e}")
            # Fallback to placeholder or skip?
            return None
            
    elif asset_type == "stock_video":
        if not PEXELS_API_KEY:
            print("Skipping stock video due to missing API key")
            return None
            
        headers = {"Authorization": PEXELS_API_KEY}
        url = f"https://api.pexels.com/videos/search?query={keyword}&per_page=1&orientation=portrait" # Portrait for mobile
        try:
            r = requests.get(url, headers=headers)
            data = r.json()
            if data.get("videos"):
                video = data["videos"][0]
                # Find best video file (usually the one with width closest to 1080)
                video_files = video["video_files"]
                # Sort by quality/size? Just take the first valid one
                video_url = video_files[0]["link"]
                download_file(video_url, filename)
            else:
                print("No videos found on Pexels.")
                return None
        except Exception as e:
            print(f"Pexels error: {e}")
            return None
            
    return filename

async def main():
    # Setup
    if not os.path.exists("assets"):
        os.makedirs("assets")
        
    topic = input("Enter video topic (default: The History of Rome): ") or "The History of Rome"
    
    # 1. Script
    scenes = await generate_script(topic)
    if not scenes:
        print("Failed to generate script.")
        return
        
    print(f"Generated {len(scenes)} scenes.")
    full_text = " ".join([s["sentence"] for s in scenes])
    
    # 2. Audio
    audio_path = "assets/voiceover.mp3"
    await generate_audio(full_text, audio_path)
    
    # 2b. Timestamps
    word_timestamps = get_word_timestamps(audio_path)
    
    # Align scenes with timestamps to determine duration
    # We map words to scenes to calculate start/end of each scene
    
    current_word_idx = 0
    video_clips = []
    
    # Define video size (e.g. 1080x1920 for Shorts)
    VIDEO_SIZE = (1080, 1920)
    
    for i, scene in enumerate(scenes):
        sentence = scene["sentence"]
        # Estimate word count
        # A simple split might mismatch Whisper's tokenization, but we'll try to sync roughly.
        # Better strategy: 
        # We know the total duration. We can just use the word timestamps.
        # We need to know WHICH words belong to THIS scene.
        # We will iterate through words and match them to the sentence.
        
        # Simple Greedy Matcher
        # Normalize sentence
        words_in_sentence = sentence.split()
        num_words = len(words_in_sentence)
        
        # Take the next num_words from timestamps
        # Safety check
        if current_word_idx >= len(word_timestamps):
            break
            
        scene_words = word_timestamps[current_word_idx : current_word_idx + num_words]
        
        # Update index
        current_word_idx += num_words
        
        if not scene_words:
            continue
            
        start_time = scene_words[0]["start"]
        end_time = scene_words[-1]["end"]
        duration = end_time - start_time
        
        # Add a tiny buffer if it's too tight or ensure continuity?
        # Ideally, end_time of this scene should be start_time of next.
        # But for visuals, we just need duration.
        
        # 3. Visuals
        asset_path = get_visual_asset(scene, i)
        
        if not asset_path or not os.path.exists(asset_path):
            print(f"Missing asset for scene {i}, skipping or using placeholder.")
            # Create a black clip or placeholder
            clip = ColorClip(size=VIDEO_SIZE, color=(0,0,0), duration=duration)
        else:
            if scene["type"] == "ai_image" or asset_path.endswith(".png"):
                # 4. Motion Engine (Ken Burns)
                clip = create_ken_burns_clip(asset_path, duration, video_size=VIDEO_SIZE)
            else:
                # Stock Video
                clip = VideoFileClip(asset_path)
                # Loop or trim
                if clip.duration < duration:
                    clip = clip.with_effects([vfx.Loop(duration=duration)])
                else:
                    clip = clip.subclipped(0, duration)
                
                # Resize to fill (Aspect Ratio)
                # video.resized(height=1920) or similar
                # Center crop
                # clip = clip.resized(height=VIDEO_SIZE[1]) # Resize height to fit
                # If width is still too small, resize by width
                w, h = clip.size
                target_w, target_h = VIDEO_SIZE
                
                scale = max(target_w/w, target_h/h)
                clip = clip.with_effects([vfx.Resize(scale)])
                clip = clip.with_position('center')
        
        # Ensure duration is exact
        clip = clip.with_duration(duration)
        video_clips.append(clip)
        
    # 6. Final Assembly
    if not video_clips:
        print("No video clips generated.")
        return

    print("Assembling video...")
    final_video = concatenate_videoclips(video_clips, method="compose")
    
    # Add Audio
    voiceover = AudioFileClip(audio_path).with_volume_scaled(1.0)
    
    # Add Background Music
    music_path = "assets/music.mp3"
    if os.path.exists(music_path):
        print("Adding background music...")
        music = AudioFileClip(music_path)
        # Loop music if shorter, or trim if longer
        if music.duration < final_video.duration:
            repeats = int(final_video.duration / music.duration) + 1
            music = concatenate_audioclips([music] * repeats).subclipped(0, final_video.duration)
        else:
            music = music.subclipped(0, final_video.duration)
            
        music = music.with_volume_scaled(0.15)
        final_audio = CompositeAudioClip([voiceover, music])
    else:
        print("No background music found (assets/music.mp3). Using voiceover only.")
        final_audio = voiceover

    final_video = final_video.with_audio(final_audio)
    
    # 5. Pop Subtitles
    print("Generating subtitles...")
    subtitle_clips = generate_dynamic_subtitles(word_timestamps, video_size=VIDEO_SIZE)
    
    # Overlay subtitles
    # We use CompositeVideoClip. 
    # Note: subtitle_clips is a list of TextClips.
    # We shouldn't dump 100 clips into CompositeVideoClip constructor if possible, 
    # but for short videos it's fine.
    
    # Combine everything
    # video_clips are already concatenated into final_video
    
    final_composition = CompositeVideoClip([final_video] + subtitle_clips, size=VIDEO_SIZE)
    
    # Write output
    output_filename = "final_video.mp4"
    print(f"Writing to {output_filename}...")
    final_composition.write_videofile(
        output_filename, 
        fps=24, 
        codec="libx264", 
        audio_codec="aac"
    )
    print("Done!")

if __name__ == "__main__":
    asyncio.run(main())
