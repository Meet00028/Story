from moviepy import *
import moviepy.video.fx as vfx
from moviepy.video.tools.subtitles import SubtitlesClip

def generate_word_level_subtitles(words, settings, video_size):
    """
    Generates a list of TextClips for word-by-word subtitles with "Pop" animation.
    
    Args:
        words (list): List of dicts with 'word', 'start', 'end'.
        settings (dict): Font, color, highlight style, etc.
        video_size (tuple): (width, height)
    """
    w_video, h_video = video_size
    
    font = settings.get("font", "Arial")
    base_fontsize = settings.get("fontSize", 70)
    default_color = settings.get("color", "white")
    stroke_color = settings.get("strokeColor", "black")
    stroke_width = settings.get("strokeWidth", 4)
    highlight_style = settings.get("highlightStyle", "none") # none, random, nouns
    pop_intensity = settings.get("popIntensity", 1.2)
    
    # Safe Zone & Positioning
    # Bottom 250px is off-limits.
    # Center vertically in the remaining space or specifically "Upper Middle".
    # Let's target the center of the screen, but slightly up to be safe.
    # Center of video is h/2.
    # Safe area bottom is h - 250.
    # Let's just center it at (w/2, h/2) for now, as that's generally safe from bottom UI if the text isn't huge.
    # Or better: (w/2, h/2 - 100)
    
    pos_x = 'center'
    pos_y = 'center' # We'll use composite positioning
    
    clips = []
    
    # Keyword logic (simple length-based for now if 'nouns' or 'random' selected)
    # Ideally we'd use NLTK for nouns, but let's stick to length > 4 for "Smart" highlighting
    
    for word_data in words:
        txt = word_data["word"].strip()
        if not txt: continue
        
        start = word_data["start"]
        end = word_data["end"]
        duration = end - start
        if duration < 0.1: duration = 0.1
        
        # 1. Determine Color
        color = default_color
        is_highlighted = False
        
        if highlight_style == "random":
            # Deterministic random based on word content
            if hash(txt) % 3 == 0: 
                color = "#FFD700" # Gold
                is_highlighted = True
        elif highlight_style == "nouns":
            # Simple heuristic: Length > 4 or Capitalized (not at start of sentence?)
            if len(txt) > 4: 
                color = "#00FF00" # Green
                is_highlighted = True
                
        # Create Base TextClip
        # We use a "Padding Container" strategy to prevent descenders (g, y, p) from being cut off.
        # CRITICAL FIX: We append a newline "\n" to the text. 
        # This forces ImageMagick to allocate height for a second line, ensuring the descenders 
        # and thick strokes of the first line are NEVER cut off.
        
        display_text = txt + "\n "

        txt_clip = TextClip(
            text=display_text,
            font=font,
            font_size=base_fontsize,
            color=color,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            method='caption',
            size=(700, None), # Wrap at 700px
            text_align='center'
        )
        
        # --- PADDING CONTAINER FIX ---
        try:
            # 1. Get dimensions of the text
            tc_w, tc_h = txt_clip.size
            
            # 2. Create a larger container
            # The text clip now has a "ghost" second line due to \n, so it's already tall.
            # We still add a bit of padding just to be safe.
            container_w = int(tc_w + 20)
            container_h = int(tc_h + 20)
            
            # 3. Create a Composite Clip
            # Because of the \n, the text is in the UPPER half of the txt_clip.
            # If we center txt_clip in the container, the text visually shifts up.
            # We want to align the TOP of the text clip somewhat near the top of the container
            # OR just center it. Centering is fine because the \n adds space at the bottom,
            # so the "visual center" of the text is slightly higher, which is good for subtitles.
            final_clip = CompositeVideoClip(
                [txt_clip.with_position('center')], 
                size=(container_w, container_h)
            ).with_duration(duration)
            
            # 4. Apply Pop Animation to the Container
            def pop_resize(t):
                if t > 0.1: return 1.0
                progress = t / 0.1
                return pop_intensity - (pop_intensity - 1.0) * progress
            
            if pop_intensity > 1.0:
                final_clip = final_clip.with_effects([vfx.Resize(pop_resize)])

            # 5. Position the Container
            # We place the container at y=850 (approx 45% from top)
            final_clip = final_clip.with_start(start).with_position(('center', 850))

            clips.append(final_clip)
            
        except Exception as e:
            print(f"Error generating subtitle for word '{txt}': {e}")
            # Fallback: try adding just the text clip if composite fails
            # But better to just skip or log to avoid crashing
            continue
        
    return clips
