import os
import json
import asyncio
import requests
import edge_tts
import whisper
from moviepy import *
from moviepy.video.tools.subtitles import SubtitlesClip
import moviepy.video.fx as vfx
import numpy as np

# Import new modules
from video_engine import generate_word_level_subtitles
from effects import create_glitch_transition, zoom_slam, whip_pan, rgb_split, vignette_overlay, film_grain

# Load Config
with open("config.json", "r") as f:
    CONFIG = json.load(f)

TEMP_DIR = "assets/temp"
os.makedirs(TEMP_DIR, exist_ok=True)

async def generate_tts(text, voice, output_path):
    for attempt in range(3):
        try:
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_path)
            return
        except Exception as e:
            print(f"TTS attempt {attempt+1} failed: {e}")
            if attempt == 2:
                raise e
            await asyncio.sleep(1)

def get_word_timestamps(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path, word_timestamps=True)
    words = []
    for segment in result["segments"]:
        for word in segment["words"]:
            words.append({
                "word": word["word"],
                "start": word["start"],
                "end": word["end"]
            })
    return words

def download_file(url, filename):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    return filename

def create_ken_burns_effect(clip, start_scale=1.0, end_scale=1.1):
    # Simple zoom effect: Resize from start_scale to end_scale over duration
    def resize_func(t):
        progress = t / clip.duration
        current_scale = start_scale + (end_scale - start_scale) * progress
        return current_scale

    return clip.with_effects([vfx.Resize(resize_func)])

def create_subtitle_clip(words, settings, video_size):
    # This is a simplified "Subtitle Pop" effect
    # We create a TextClip for each word or group of words
    # For "CapCut style", we often want one word at a time or a few.
    # Let's do word-by-word for now as requested.
    
    subtitle_clips = []
    font = settings.get("font", "Arial")
    fontsize = settings.get("fontSize", 60)
    color = settings.get("color", "white")
    stroke_color = settings.get("strokeColor", "black")
    stroke_width = settings.get("strokeWidth", 2)
    position = settings.get("position", "center") # top, center, bottom
    
    # Map position to Y coordinate
    w, h = video_size
    y_pos = 'center'
    if position == 'top': y_pos = 100
    elif position == 'bottom': y_pos = h - 150
    
    for word_data in words:
        txt = word_data["word"].strip()
        if not txt: continue
        
        start = word_data["start"]
        end = word_data["end"]
        duration = end - start
        if duration < 0.1: duration = 0.1 # Minimum duration
        
        txt_clip = (TextClip(text=txt, font=font, font_size=fontsize, color=color, stroke_color=stroke_color, stroke_width=stroke_width, size=(w, None), method='caption')
                    .with_position(('center', y_pos))
                    .with_start(start)
                    .with_duration(duration))
        
        # Add a small pop animation (scale up slightly) - tricky with simple TextClip in v2
        # We'll skip complex pop animation for now and stick to word-by-word timing
        subtitle_clips.append(txt_clip)
        
    return subtitle_clips

async def render_video(data):
    # Unpack data
    global_settings = data.get("global_settings", {})
    scenes = data.get("scenes", [])
    
    voice = global_settings.get("voice", "en-US-ChristopherNeural")
    music_vol = global_settings.get("music_vol", 0.1)
    
    final_clips = []
    current_time = 0
    all_audio_clips = []
    all_subtitle_clips = []
    
    for i, scene in enumerate(scenes):
        text = scene.get("text", "")
        media_type = scene.get("media_type", "gameplay") # gameplay, pexels
        media_url = scene.get("media_url", "")
        transition = scene.get("transition", "none")
        
        # 1. Generate Audio
        audio_filename = f"{TEMP_DIR}/scene_{i}.mp3"
        await generate_tts(text, voice, audio_filename)
        audio_clip = AudioFileClip(audio_filename)
        all_audio_clips.append(audio_clip)
        scene_duration = audio_clip.duration
        
        # 2. Get Word Timestamps (offset by current_time)
        # Note: Whisper is slow. For production, run once on full audio. 
        # Here we do per scene for modularity, but it might be choppy.
        # Optimization: Concatenate text and run TTS/Whisper once? 
        # User wants "Scene Editor", so per-scene is logical but maybe slower.
        # Let's stick to per-scene for now.
        words = get_word_timestamps(audio_filename)
        # Adjust timestamps
        for w in words:
            w["start"] += current_time
            w["end"] += current_time
        
        # scene_subs = create_subtitle_clip(words, data.get("subtitle_settings", {}), (1080, 1920))
        # all_subtitle_clips.extend(scene_subs)
        
        # 3. Prepare Visual
        visual_clip = None
        if media_type == "gameplay":
            # Load default assets
            bg_path = "assets/backgrounds/minecraft_parkour.mp4" # Default
            
            # Safe check for media_url
            url_lower = media_url.lower() if media_url else ""
            
            if "minecraft" in url_lower: bg_path = "assets/backgrounds/minecraft_parkour.mp4"
            elif "subway" in url_lower: bg_path = "assets/backgrounds/subway_surfers.mp4"
            elif "gta" in url_lower: bg_path = "assets/backgrounds/gta_v.mp4" # Assuming this exists or we map to existing
            
            # Fallback if file doesn't exist
            if not os.path.exists(bg_path):
                 # Create a dummy if missing
                 bg_path = "assets/backgrounds/minecraft_parkour.mp4"
            
            if os.path.exists(bg_path):
                bg_clip = VideoFileClip(bg_path)
                visual_clip = bg_clip.with_effects([vfx.Loop(duration=scene_duration)])
            else:
                visual_clip = ColorClip(size=(1080, 1920), color=(0,0,0), duration=scene_duration)

        elif media_type == "pexels":
            if media_url:
                local_filename = f"{TEMP_DIR}/pexels_{i}.mp4"
                if not os.path.exists(local_filename):
                    download_file(media_url, local_filename)
                
                bg_clip = VideoFileClip(local_filename)
                # Resize to cover 1080x1920 (9:16)
                # We need to crop to aspect ratio then resize
                bg_clip = bg_clip.with_effects([vfx.Crop(width=bg_clip.h * (9/16), height=bg_clip.h, x_center=bg_clip.w/2, y_center=bg_clip.h/2)])
                bg_clip = bg_clip.with_effects([vfx.Resize(height=1920)]) # Width will be 1080
                
                # Loop if too short
                if bg_clip.duration < scene_duration:
                    bg_clip = bg_clip.with_effects([vfx.Loop(duration=scene_duration)])
                else:
                    bg_clip = bg_clip.with_duration(scene_duration)
                
                # Apply Ken Burns or new Effects
                effect = scene.get("effect", "none")
                if effect == "zoom_in":
                    bg_clip = create_ken_burns_effect(bg_clip)
                elif effect == "zoom_slam":
                    bg_clip = zoom_slam(bg_clip)
                elif effect == "whip_pan":
                    bg_clip = whip_pan(bg_clip)
                elif effect == "rgb_split":
                    bg_clip = rgb_split(bg_clip)
                elif effect == "vignette":
                    bg_clip = vignette_overlay(bg_clip)
                elif effect == "film_grain":
                    bg_clip = film_grain(bg_clip)
                
                visual_clip = bg_clip
            else:
                visual_clip = ColorClip(size=(1080, 1920), color=(50,50,50), duration=scene_duration)

        # Apply Transition IN
        # Options: "fade", "glitch", "zoom_in", "whip_pan", "fade_black", "flash_white"
        
        if transition == "fade":
            visual_clip = visual_clip.with_effects([vfx.CrossFadeIn(0.5)])
            
        elif transition == "fade_black":
            # Standard FadeIn (from black)
            visual_clip = visual_clip.with_effects([vfx.FadeIn(0.5)])
            
        elif transition == "flash_white":
            # Composite a white clip on top that fades out
            white_flash = ColorClip(size=(1080, 1920), color=(255,255,255), duration=0.5)
            # Fade out the white clip
            white_flash = white_flash.with_effects([vfx.CrossFadeOut(0.5)])
            # Composite: White on top of visual
            visual_clip = CompositeVideoClip([visual_clip, white_flash.with_start(0)])
            
        elif transition == "zoom_in":
            # Scale from 1.5 to 1.0 over 0.5s
            def zoom_in_func(t):
                if t > 0.5: return 1.0
                progress = t / 0.5
                return 1.5 - (0.5 * progress)
            visual_clip = visual_clip.with_effects([vfx.Resize(zoom_in_func)])
            
        elif transition == "whip_pan":
            # Slide in from Left (-1080 to 0) over 0.3s
            w, h = 1080, 1920
            def slide_in(t):
                if t > 0.3: return (0, 0)
                progress = t / 0.3
                # Exponential ease out
                p = 1 - (1 - progress)**2
                return (-w + (w * p), 0)
            
            # Note: with_position requires the clip to be in a CompositeVideoClip usually,
            # but if we just apply it, it might work if we composite it later.
            # However, for a single clip, it defines its position in the final composite.
            # Since we concatenate later, this might be tricky.
            # But let's apply it. When we concatenate, it respects position?
            # Actually concatenate_videoclips might ignore position if not compositing.
            # Safer: Put it in a CompositeVideoClip of the same size.
            visual_clip = CompositeVideoClip([visual_clip.with_position(slide_in)], size=(1080, 1920)).with_duration(scene_duration)

        elif transition == "glitch":
            # Apply glitch to first 0.5s
            def glitch_filter(get_frame, t):
                frame = get_frame(t)
                if t < 0.5 and np.random.random() > 0.6:
                    # Random RGB Shift
                    offset = np.random.randint(-30, 30)
                    frame = np.roll(frame, offset, axis=1)
                    # Random Invert
                    if np.random.random() > 0.8:
                        frame = 255 - frame
                return frame
            visual_clip = visual_clip.transform(glitch_filter)
        
        visual_clip = visual_clip.with_audio(audio_clip)
        final_clips.append(visual_clip)
        
        # Add Subtitles (using new engine)
        scene_subs = generate_word_level_subtitles(words, data.get("subtitle_settings", {}), (1080, 1920))
        all_subtitle_clips.extend(scene_subs)
        
        current_time += scene_duration

    # Concatenate
    # Check if we need to apply transitions between clips?
    # The 'transition' property in 'scene' usually means "Transition FROM previous scene INTO this one".
    # Since we are iterating, we can apply transition effects.
    # But simple concatenation is easier.
    # Let's rely on what we have (CrossFadeIn handles start).
    # Glitch transition needs access to PREVIOUS clip.
    # We'll skip complex inter-clip transitions for now unless we refactor the loop.
    # But we implemented create_glitch_transition in effects.py.
    # Let's try to use it if requested.
    
    # Advanced: If transition is 'glitch', we need to blend with previous.
    # This requires a more complex loop where we don't just append to list.
    # For now, let's stick to simple list concatenation + CrossFadeIn.
   # Concatenate
    final_video = concatenate_videoclips(final_clips, method="compose")
    
    # Overlay Subtitles
    final_video = CompositeVideoClip([final_video] + all_subtitle_clips)
    
    # Add Background Music (if provided)
    # skipped for brevity/complexity, can add if requested or just rely on global mix
    
    output_filename = "output.mp4"
    final_video.write_videofile(output_filename, fps=24, codec="libx264", audio_codec="aac")
    return output_filename
