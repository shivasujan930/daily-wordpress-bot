import openai
import os
from dotenv import load_dotenv

# ——— Load credentials ———————————————————————————————
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = openai.OpenAI(api_key=OPENAI_API_KEY)

# ——— Load the 20-second voiceover script ———————————————————
def load_narration():
    with open("video_prompt.txt", "r", encoding="utf-8") as f:
        return f.read().strip()

# ——— Split into sentences ——————————————————————————————————
def split_into_scenes(script_text):
    import re
    # Split by sentence-ending punctuation
    return [s.strip() for s in re.split(r'[.?!]\s+', script_text) if s.strip()]

# ——— Generate visual prompt for each scene —————————————————
def generate_visual_prompt(sentence):
    system_msg = "You are a professional visual prompt engineer for AI-generated imagery."
    user_prompt = (
        "Convert the following narration sentence into a DALL·E-compatible visual prompt. "
        "Focus on the visual elements described or implied. Use descriptive, specific nouns and adjectives. "
        "Avoid abstract or non-visual words. Example: narration → 'The Federal Reserve raised rates today' becomes → 'a tall modern government building labeled Federal Reserve, surrounded by falling red arrows and interest rate charts.'\n\n"
        f"NARRATION: {sentence}\nVISUAL PROMPT:"
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.5
    )

    return response.choices[0].message.content.strip()

# ——— Save visual prompts ————————————————————————————————
def save_prompts(prompts):
    os.makedirs("visual_prompts", exist_ok=True)
    for i, prompt in enumerate(prompts, start=1):
        filename = f"visual_prompts/scene_{i}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(prompt)
    print(f"✅ Saved {len(prompts)} visual prompts in /visual_prompts")

# ——— Main execution ————————————————————————————————
if __name__ == "__main__":
    script = load_narration()
    scenes = split_into_scenes(script)
    
    visual_prompts = []
    for i, sentence in enumerate(scenes, start=1):
        print(f"🧠 Converting scene {i}: {sentence}")
        prompt = generate_visual_prompt(sentence)
        print(f"   → 🎨 {prompt}")
        visual_prompts.append(prompt)
    
    save_prompts(visual_prompts)
