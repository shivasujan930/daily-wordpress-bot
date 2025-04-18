from moviepy.editor import *
import os

# ——— Config ——————————————————————————————
IMG_DIR = "ai_images"
AUDIO_FILE = "voiceover.mp3"
OUTPUT_VIDEO = "video_output.mp4"

def load_images_sorted():
    files = sorted([
        f for f in os.listdir(IMG_DIR)
        if f.endswith(".png") or f.endswith(".jpg")
    ])
    return [os.path.join(IMG_DIR, f) for f in files]

def create_ken_burns_clip(image_path, duration):
    img = ImageClip(image_path)
    img = img.set_duration(duration)

    # Apply slow zoom-in + slight pan
    return img.resize(height=1080).fx(vfx.crop, x1=10, y1=10, x2=10, y2=10).fx(vfx.fadein, 0.5).fx(vfx.fadeout, 0.5)

def generate_video():
    image_paths = load_images_sorted()
    if not image_paths:
        print("❌ No images found.")
        return

    audio = AudioFileClip(AUDIO_FILE)
    total_duration = audio.duration
    duration_per_scene = total_duration / len(image_paths)

    clips = [create_ken_burns_clip(path, duration_per_scene) for path in image_paths]
    final_video = concatenate_videoclips(clips, method="compose")
    final_video = final_video.set_audio(audio)

    final_video.write_videofile(OUTPUT_VIDEO, fps=24, codec="libx264", audio_codec="aac")
    print(f"✅ Video saved to {OUTPUT_VIDEO}")

# ——— Run ————————————————————————————————————
if __name__ == "__main__":
    generate_video()
