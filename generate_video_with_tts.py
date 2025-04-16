from gtts import gTTS
import os
import subprocess

# Read video script
with open("video_script.txt", "r") as f:
    script_text = f.read()

# Generate voiceover
tts = gTTS(text=script_text, lang='en')
tts.save("voiceover.mp3")
print("✅ Voiceover saved as voiceover.mp3")

# Use a background image or stock video (static image example here)
background = "background.jpg"  # Replace with your actual image path

# Create video from image + voiceover
output_video = "short_video.mp4"
cmd = [
    "ffmpeg",
    "-loop", "1",
    "-i", background,
    "-i", "voiceover.mp3",
    "-c:v", "libx264",
    "-tune", "stillimage",
    "-c:a", "aac",
    "-b:a", "192k",
    "-pix_fmt", "yuv420p",
    "-shortest",
    "-y",  # Overwrite if exists
    output_video
]

subprocess.run(cmd, check=True)
print(f"🎬 Video generated: {output_video}")
