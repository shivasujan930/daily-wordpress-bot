import openai
import os
from datetime import datetime
from dotenv import load_dotenv

# Load credentials
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Read summary from file
def read_summary():
    with open("blog_summary.txt", "r", encoding="utf-8") as file:
        return file.read()

# Generate and save/append the video script
def generate_video_script(summary):
    prompt = (
        "Using the following 100-word summary, write a 30-second video script "
        "suitable for a professional financial news reel:\n\n"
        f"{summary}\n\n"
        "The script should be concise, engaging, and include cues for on-screen text."
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a professional video script writer."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    script = response.choices[0].message.content.strip()

    # Append to history file with timestamp
    history_path = "video_script_history.txt"
    with open(history_path, "a", encoding="utf-8") as hist:
        hist.write("================================================================================\n")
        hist.write(f"VIDEO SCRIPT — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        hist.write("================================================================================\n")
        hist.write(script + "\n\n")

    # Also save the latest script to a separate file
    with open("video_script.txt", "w", encoding="utf-8") as f:
        f.write(script)

    print("\n✅ 30-second video script generated and appended to 'video_script_history.txt'.")

# Main execution
if __name__ == "__main__":
    summary = read_summary()
    generate_video_script(summary)
