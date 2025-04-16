import os
import openai
import requests
from dotenv import load_dotenv

load_dotenv()

# Load credentials from environment
openai.api_key = os.getenv("OPENAI_API_KEY")
wp_username = os.getenv("WP_USERNAME")
wp_password = os.getenv("WP_APP_PASSWORD")
wp_site_url = os.getenv("WP_SITE_URL")

# Step 1: Generate blog content and summary
def generate_blog():
    prompt = "Generate a 600-word blog post on a trending business topic and a 250-word summary."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    content = response.choices[0].message["content"]
    
    # Split into blog and summary
    blog, summary = content.split("250-word summary:", 1)
    return blog.strip(), summary.strip()

# Step 2: Post blog to WordPress
def post_to_wordpress(title, content):
    url = f"{wp_site_url}/wp-json/wp/v2/posts"
    auth = (wp_username, wp_password)
    headers = {"Content-Type": "application/json"}
    data = {
        "title": title,
        "content": content,
        "status": "publish"
    }
    response = requests.post(url, auth=auth, headers=headers, json=data)
    print("WordPress response:", response.status_code, response.text)
    response.raise_for_status()

# Step 3: Save blog summary for video generation
def save_summary_to_file(summary):
    with open("blog_summary.txt", "w") as f:
        f.write(summary)

# Run
if __name__ == "__main__":
    blog_text, summary_text = generate_blog()
    save_summary_to_file(summary_text)
    post_to_wordpress("Today's Business Insights", blog_text)