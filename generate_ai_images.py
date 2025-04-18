import openai
import os
from dotenv import load_dotenv
from time import sleep

# ——— Load credentials ——————————————————————————————————————
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# ——— Config ——————————————————————————————————————————————
PROMPT_FOLDER = "visual_prompts"
OUTPUT_FOLDER = "ai_images"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ——— Read visual prompt from file ————————————————————————
def read_prompt(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read().strip()

# ——— Generate AI image using OpenAI's DALL·E ————————————
def generate_image(prompt, output_path):
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        image_url = response.data[0].url

        # Download the image
        import requests
        img_data = requests.get(image_url).content
        with open(output_path, 'wb') as f:
            f.write(img_data)
        print(f"✅ Saved image to {output_path}")

    except Exception as e:
        print(f"❌ Failed to generate image: {e}")

# ——— Main execution ———————————————————————————————————————
if __name__ == "__main__":
    prompt_files = sorted([
        f for f in os.listdir(PROMPT_FOLDER)
        if f.endswith(".txt")
    ])

    for i, filename in enumerate(prompt_files, start=1):
        prompt_path = os.path.join(PROMPT_FOLDER, filename)
        prompt_text = read_prompt(prompt_path)
        print(f"🎨 Generating image for scene {i}...")

        output_file = os.path.join(OUTPUT_FOLDER, f"scene_{i}.png")
        generate_image(prompt_text, output_file)
        
        sleep(1)  # avoid rate limits
