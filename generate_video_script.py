import openai
import os
from datetime import datetime
from dotenv import load_dotenv

# ——— Load credentials —————————————————————————————
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ——— Initialize OpenAI client —————————————————————————
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# ——— Read the 100‑word blog summary ——————————————————————
def read_summary():
    with open("blog_summary.txt", "r", encoding="utf-8") as file:
        return file.read().strip()

# ——— Craft and save a 20‑second video prompt —————————————————
def generate_video_prompt(summary):
    # Clear, creative instructions for the video generator:
    prompt_text = (
        "You are a top‑tier video prompt engineer. "
        "Using the following 100‑word summary, craft a single text prompt "
        "that will instruct an AI video‑generation tool to produce a **20‑second** "
        "professional financial news video. Your prompt should:\n"
        "  • Faithfully follow the summary’s core message and data points.\n"
        "  • Describe scene transitions and visual style (e.g., stock tickers, graphs, newsroom b-roll).\n"
        "  • Specify pacing cues (e.g., quick cuts, on-screen text overlays at key moments).\n"
        "  • Indicate tone and color palette (e.g., sleek, corporate, blue‑grey tones).\n\n"
        f"SUMMARY:\n{summary}\n\n"
        "Now write the final creative prompt:"
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a professional video prompt writer."},
            {"role": "user",   "content": prompt_text}
        ],
        temperature=0.7
    )

    video_prompt = response.choices[0].message.content.strip()

    # — Append to history with timestamp —
    history_path = "video_prompt_history.txt"
    with open(history_path, "a", encoding="utf-8") as hist:
        hist.write("================================================================================\n")
        hist.write(f"VIDEO PROMPT — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        hist.write("================================================================================\n")
        hist.write(video_prompt + "\n\n")

    # — Save latest prompt —
    with open("video_prompt.txt", "w", encoding="utf-8") as f:
        f.write(video_prompt)

    print("\n✅ 20‑second video prompt generated and appended to 'video_prompt_history.txt'.")

# ——— Main execution ————————————————————————————————
if __name__ == "__main__":
    summary = read_summary()
    generate_video_prompt(summary)
