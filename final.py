import requests
import datetime
import base64
import os
from dotenv import load_dotenv

# Load environment variables from .env file
# Load environment variables from .env file
load_dotenv()
print("OpenAI key loaded as:", os.getenv("OPENAI_API_KEY"))

# Environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WP_USERNAME = os.getenv("WP_USERNAME")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")
WP_SITE_URL = os.getenv("WP_SITE_URL")


# Prompt for the blog post
PROMPT = "Write a 250-word news-style blog post about the latest in business news. Make it informative, engaging, and easy to understand."

# --- Step 1: Generate blog content using OpenAI ---
def generate_blog():
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": PROMPT}],
        "temperature": 0.7
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    response.raise_for_status()
    content = response.json()
    return content['choices'][0]['message']['content']

# --- Step 2: Publish blog post to WordPress ---
def post_to_wordpress(title, content):
    auth_header = base64.b64encode(f"{WP_USERNAME}:{WP_APP_PASSWORD}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/json"
    }
    data = {
        "title": title,
        "content": content,
        "status": "publish"
    }
    response = requests.post(f"{WP_SITE_URL}/wp-json/wp/v2/posts", headers=headers, json=data)
    response.raise_for_status()
    return response.json()

# --- Main ---
if __name__ == "__main__":
    blog_content = generate_blog()
    today_title = datetime.date.today().strftime("%Y-%m-%d") + " - Daily Business News"
    result = post_to_wordpress(today_title, blog_content)
    print("✅ Blog posted:", result['link'])