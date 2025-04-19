import openai
import requests
import os
from dotenv import load_dotenv

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_blog_poster_from_text(blog_text, output_path="blog_poster.png"):
    """Generate a DALL·E blog poster based on blog content"""
    try:
        print("🧠 Generating poster prompt...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You write creative visual prompts for DALL·E to generate blog posters."},
                {"role": "user", "content": f"Write a modern, visually engaging poster prompt for a blog with this content:\n\n{blog_text}"}
            ],
            temperature=0.7
        )
        prompt = response.choices[0].message.content.strip()
        print(f"🎯 Prompt: {prompt}")

        print("🎨 Generating poster image via DALL·E...")
        image_response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1792x1024"  # ✅ Best size for blog posters
        )
        image_url = image_response.data[0].url
        img_data = requests.get(image_url).content

        with open(output_path, "wb") as f:
            f.write(img_data)

        print(f"✅ Poster saved to {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Failed to generate poster from blog text: {e}")
        return None

def upload_image_to_wp(image_path):
    """Upload image to WordPress and return media object"""
    WP_USERNAME = os.getenv("WP_USERNAME")
    WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")
    WP_SITE_URL = os.getenv("WP_SITE_URL")

    if not os.path.exists(image_path):
        print("❌ Image not found:", image_path)
        return {}

    try:
        media_endpoint = f"{WP_SITE_URL}/wp-json/wp/v2/media"
        headers = {
            "Authorization": "Basic " + os.environ.get("WP_AUTH_HEADER"),
            "Content-Disposition": f'attachment; filename="{os.path.basename(image_path)}"',
            "Content-Type": "image/png"
        }

        # fallback if WP_AUTH_HEADER is not set
        if not headers["Authorization"]:
            import base64
            token = base64.b64encode(f"{WP_USERNAME}:{WP_APP_PASSWORD}".encode()).decode()
            headers["Authorization"] = f"Basic {token}"

        with open(image_path, "rb") as img:
            response = requests.post(media_endpoint, headers=headers, data=img)

        if response.status_code == 201:
            print("✅ Uploaded poster to WordPress")
            return response.json()
        else:
            print(f"❌ Failed to upload poster: {response.text}")
            return {}

    except Exception as e:
        print(f"❌ Upload error: {e}")
        return {}
