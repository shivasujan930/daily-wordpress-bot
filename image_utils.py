import openai
import requests
import os
import base64
from dotenv import load_dotenv

# ——— Load API keys and WordPress credentials ————————————————
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WP_USERNAME = os.getenv("WP_USERNAME")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")
WP_SITE_URL = os.getenv("WP_SITE_URL")

client = openai.OpenAI(api_key=OPENAI_API_KEY)

# ——— Step 1: Generate visual prompt from blog content ——————————————
def generate_prompt_from_blog(blog_path="blog_post.txt"):
    if not os.path.exists(blog_path):
        print("❌ blog_post.txt not found.")
        return "A professional blog poster with financial charts and a blue-gray color scheme."

    with open(blog_path, "r", encoding="utf-8") as f:
        blog_text = f.read().strip()

    print("🧠 Generating visual prompt from blog content...")

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You write creative visual prompts for DALL·E to generate blog posters."},
                {"role": "user", "content": f"Write a professional, visually engaging image prompt for a financial blog poster based on this content:\n\n{blog_text}"}
            ],
            temperature=0.7
        )

        prompt = response.choices[0].message.content.strip()
        print(f"🎯 Poster prompt generated:\n{prompt}")
        return prompt

    except Exception as e:
        print(f"❌ Failed to generate poster prompt: {e}")
        return "A blog poster with a stock market theme and business visuals"

# ——— Step 2: Generate DALL·E poster image —————————————————————
def generate_blog_poster(prompt, output_path="blog_poster.png"):
    print("🎨 Generating poster image from DALL·E...")

    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024"
        )

        image_url = response.data[0].url
        img_data = requests.get(image_url).content

        with open(output_path, "wb") as f:
            f.write(img_data)

        print(f"✅ Poster image saved to {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Failed to generate poster image: {e}")
        return None

# ——— Step 3: Upload to WordPress + Set as Featured Image ——————————
def upload_image_to_wp(image_path):
    if not os.path.exists(image_path):
        print("❌ Image file not found.")
        return None

    print("☁️ Uploading poster to WordPress media...")

    media_endpoint = f"{WP_SITE_URL}/wp-json/wp/v2/media"
    auth = base64.b64encode(f"{WP_USERNAME}:{WP_APP_PASSWORD}".encode()).decode()

    headers = {
        "Authorization": f"Basic {auth}",
        "Content-Disposition": f'attachment; filename="{os.path.basename(image_path)}"',
        "Content-Type": "image/png"
    }

    with open(image_path, "rb") as f:
        response = requests.post(media_endpoint, headers=headers, data=f)

    if response.status_code == 201:
        media_id = response.json()["id"]
        image_url = response.json()["source_url"]
        print(f"✅ Uploaded poster image to WordPress: {image_url}")
        return media_id
    else:
        print(f"❌ Failed to upload image: {response.text}")
        return None

# ——— Step 4: Set Featured Image on Latest Post ——————————————
def set_featured_image(media_id):
    if not media_id:
        return

    print("🌟 Setting image as blog featured image...")

    auth = base64.b64encode(f"{WP_USERNAME}:{WP_APP_PASSWORD}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/json"
    }

    # Get latest post ID
    posts = requests.get(f"{WP_SITE_URL}/wp-json/wp/v2/posts", headers=headers).json()
    if not posts:
        print("❌ No posts found.")
        return

    post_id = posts[0]['id']

    # Set featured media
    payload = {"featured_media": media_id}
    resp = requests.post(f"{WP_SITE_URL}/wp-json/wp/v2/posts/{post_id}", headers=headers, json=payload)

    if resp.status_code == 200:
        print("✅ Featured image set successfully.")
    else:
        print(f"❌ Failed to set featured image: {resp.text}")

# ——— Main Execution ————————————————————————————————————————
if __name__ == "__main__":
    prompt = generate_prompt_from_blog()
    poster_path = generate_blog_poster(prompt)

    if poster_path:
        media_id = upload_image_to_wp(poster_path)
        set_featured_image(media_id)
