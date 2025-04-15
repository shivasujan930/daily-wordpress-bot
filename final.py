import os
import requests
import openai
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables (only works locally with a .env file)
load_dotenv()

# Load sensitive credentials from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WP_USERNAME = os.getenv("WP_USERNAME")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")
WP_SITE_URL = os.getenv("WP_SITE_URL")

print("OPENAI_API_KEY:", bool(OPENAI_API_KEY))
print("WP_USERNAME:", bool(WP_USERNAME))
print("WP_APP_PASSWORD:", bool(WP_APP_PASSWORD))
print("WP_SITE_URL:", bool(WP_SITE_URL))

# Validate environment
if not all([OPENAI_API_KEY, WP_USERNAME, WP_APP_PASSWORD, WP_SITE_URL]):
    raise EnvironmentError("Missing one or more required environment variables.")

# Set OpenAI key
openai.api_key = OPENAI_API_KEY

def generate_blog():
    """Generate blog content using OpenAI GPT model"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful AI writing daily blog posts."},
                {"role": "user", "content": "Write a 300-word blog post about the latest tech news."}
            ],
            temperature=0.7,
            max_tokens=600
        )
        blog_content = response.choices[0].message["content"]
        return blog_content
    except Exception as e:
        print("❌ Error generating blog:", str(e))
        raise

def post_to_wordpress(title, content):
    """Publish the blog content to WordPress"""
    url = f"{WP_SITE_URL}/wp-json/wp/v2/posts"
    auth = (WP_USERNAME, WP_APP_PASSWORD)
    headers = {"Content-Type": "application/json"}

    payload = {
        "title": title,
        "content": content,
        "status": "publish"  # Change to 'draft' if you want to manually review before publishing
    }

    try:
        response = requests.post(url, auth=auth, headers=headers, json=payload)
        response.raise_for_status()
        print("✅ Blog posted successfully:", response.json().get("link"))
    except requests.exceptions.HTTPError as err:
        print("❌ Failed to post to WordPress:", err.response.text)
        raise
    except Exception as e:
        print("❌ Unexpected error posting to WordPress:", str(e))
        raise

def main():
    print("🚀 Generating blog post...")
    blog_content = generate_blog()

    today = datetime.now().strftime("%B %d, %Y")
    title = f"Daily Tech Digest – {today}"

    print("📝 Posting blog to WordPress...")
    post_to_wordpress(title, blog_content)

if __name__ == "__main__":
    main()
