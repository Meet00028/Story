from moviepy import *
import os

ASSETS_DIR = "assets/backgrounds"
os.makedirs(ASSETS_DIR, exist_ok=True)

# Create a simple color clip as a dummy background
clip = ColorClip(size=(1080, 1920), color=(0, 255, 0), duration=5)
clip.write_videofile(os.path.join(ASSETS_DIR, "minecraft_parkour.mp4"), fps=24)
clip = ColorClip(size=(1080, 1920), color=(255, 0, 0), duration=5)
clip.write_videofile(os.path.join(ASSETS_DIR, "subway_surfers.mp4"), fps=24)
