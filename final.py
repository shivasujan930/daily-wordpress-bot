import os
import openai
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Credentials
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WP_USERNAME = os.getenv("WP_USERNAME")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")
WP_SITE_URL = os.getenv("WP_SITE_URL")

# Initialize OpenAI client (NEW SDK format)
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Step 1: Generate blog + summary
def generate_blog():
    prompt = (
        "Write a 600-word blog post on a trending business topic. Then write a 250-word summary "
        "starting with 'SUMMARY:'."
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that writes blog content."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    full_text = response.choices[0].message.content
    blog, summary = full_text.split("SUMMARY:", 1)
    return blog.strip(), summary.strip()

# Step 2: Post blog to WordPress
def post_to_wordpress(title, content):
    post_url = f"{WP_SITE_URL}/wp-json/wp/v2/posts"
    headers = {"Content-Type": "application/json"}
    payload = {
        "title": title,
        "content": content,
        "status": "publish"
    }

    response = requests.post(post_url, headers=headers, json=payload, auth=(WP_USERNAME, WP_APP_PASSWORD))
    print("WordPress Response:", response.status_code, response.text)
    response.raise_for_status()

# Step 3: Save summary to file
def save_summary(summary_text):
    with open("blog_summary.txt", "w") as f:
        f.write(summary_text)

# Main Execution
if __name__ == "__main__":
    blog_text, summary_text = generate_blog()
    save_summary(summary_text)
    post_to_wordpress("Today's Business Insights", blog_text)
