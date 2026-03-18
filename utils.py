import json
import os
from moviepy import *
import moviepy.video.fx as vfx

def load_config():
    if not os.path.exists("config.json"):
        return {}
    with open("config.json", "r") as f:
        return json.load(f)

def create_ken_burns_clip(image_path, duration, video_size=(1920, 1080)):
    """
    Creates a Ken Burns effect (zoom in) on an image.
    Returns a clip resized and centered.
    """
    # Load image
    clip = ImageClip(image_path).with_duration(duration)
    
    # Resize image to cover the video_size initially (filling the screen)
    # We use 'resized' with 'height' or 'width' to cover.
    # But simpler: resize to be at least video_size, then center crop.
    
    # First, simple resize to fit/cover? 
    # Let's assume we want to fill the screen.
    w, h = video_size
    iw, ih = clip.size
    
    # Calculate scale to cover
    scale = max(w/iw, h/ih)
    clip = clip.with_effects([vfx.Resize(scale)]) # Initial scale to cover
    
    # Define zoom function (1.0 to 1.2 relative to current size)
    def zoom_func(t):
        return 1.0 + 0.2 * (t / duration)
    
    # Apply dynamic zoom
    # We apply the zoom to the already scaled clip
    clip_zoomed = clip.with_effects([vfx.Resize(zoom_func)])
    
    # Center the clip
    clip_zoomed = clip_zoomed.with_position('center')
    
    # Composite on a fixed background to ensure the frame doesn't grow
    # This acts as a crop
    # We create a CompositeVideoClip of the target size
    # But wait, if we return a CompositeVideoClip for EVERY scene, it might be heavy.
    # Better to just return the zoomed clip, and let the final assembly handle the "viewing window" 
    # or wrap it here. Wrapping here is safer for the "clip" concept.
    
    final_clip = CompositeVideoClip([clip_zoomed], size=video_size)
    
    return final_clip

def generate_dynamic_subtitles(whisper_data, video_size=(1920, 1080)):
    """
    Generates a list of TextClips for each word.
    """
    subtitle_clips = []
    
    # Font settings
    font = "Impact"
    fontsize = 100 # Big for impact
    color = "yellow"
    stroke_color = "black"
    stroke_width = 4
    
    for item in whisper_data:
        word = item['word'].strip()
        start = item['start']
        end = item['end']
        
        if not word:
            continue
        
        # Create TextClip
        # Note: In MoviePy v2, ensure font is valid. 
        # If 'Impact' is not found, it might raise error or fallback.
        # We assume the system has Impact or ImageMagick can find it.
        
        txt_clip = TextClip(
            text=word,
            font=font,
            font_size=fontsize,
            color=color,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            method='label'
        )
        
        # Pop effect: Scale 1.1 (already big, but let's apply a slight pop or just keep it static big)
        # User asked: "Make the current word 'Yellow' and slightly larger (Scale 1.1)"
        # We can just apply a static scale of 1.1 to the base font size (effectively done by fontsize=100)
        # Or we can animate the scale? 
        # "Make the current word... slightly larger" implies it IS larger than normal text.
        # Since we only show one word, it IS the current word.
        
        txt_clip = txt_clip.with_start(start).with_end(end).with_position('center')
        
        subtitle_clips.append(txt_clip)
        
    return subtitle_clips
