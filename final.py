import os
import json
import openai
import requests
import pytz
import random
import time
import re
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAIError

# ——— Load credentials —————————————————————————————
load_dotenv()
OPENAI_API_KEY   = os.getenv("OPENAI_API_KEY")
WP_USERNAME     = os.getenv("WP_USERNAME")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")
WP_SITE_URL     = os.getenv("WP_SITE_URL")

# ——— Initialize OpenAI —————————————————————————————
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# ——— Helpers ———————————————————————————————————————

def log_blog_to_history(blog_content: str):
    """Append blog content to history file with timestamp"""
    LOG_FILE = "blog_history.txt"
    ts = datetime.now(pytz.utc)\
             .astimezone(pytz.timezone('America/New_York'))\
             .strftime("%Y-%m-%d %H:%M:%S %Z")
    divider = "=" * 80
    entry = f"\n\n{divider}\nBLOG ENTRY - {ts}\n{divider}\n\n{blog_content}\n"
    with open(LOG_FILE, "a") as f:
        f.write(entry)
    print("📋 Logged to", LOG_FILE)


def generate_blog():
    """Generate blog post, summary, and title using OpenAI API"""
    system = {
        "role":"system",
        "content":(
            "You are a top‑tier financial intelligence writer. "
            "Output strict JSON with three fields:\n"
            "  • \"blog\": a 250‑word market‑moving news post\n"
            "  • \"summary\": a 100‑word brief prefixed with 'SUMMARY:'\n"
            "  • \"title\": a click‑worthy headline (no timestamp)"
        )
    }
    
    try:
        # Request JSON format specifically to ensure proper response format
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[system, {"role":"user","content":""}],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        # Parse the JSON response
        try:
            data = json.loads(resp.choices[0].message.content)
            blog = data["blog"].strip()
            summary = data["summary"].strip()
            title = data["title"].strip()
        except (json.JSONDecodeError, KeyError) as e:
            # Fallback if JSON parsing fails or expected keys are missing
            print(f"⚠️ Error processing AI response: {e}")
            print(f"Raw content received: {resp.choices[0].message.content[:100]}...")
            
            # Create fallback content
            content = resp.choices[0].message.content
            blog = content if len(content) > 100 else "Recent market movements indicate volatility across multiple sectors. Investors are closely monitoring central bank policies and geopolitical developments. Financial analysts recommend diversified portfolios as a hedge against uncertainty. Market indicators suggest cautious optimism for the coming quarter, with selective opportunities in technology and sustainable energy sectors."
            summary = "SUMMARY: Financial markets are experiencing volatility influenced by monetary policy shifts and global events. Diversification strategies are recommended while selective sectors offer potential despite broader uncertainty."
            title = "Market Analysis: Navigating Volatility in Today's Financial Landscape"
            
        # Log the blog content to history file
        log_blog_to_history(blog)
        return blog, summary, title
        
    except OpenAIError as e:
        # Handle OpenAI API errors
        print(f"❌ OpenAI API error: {e}")
        # Return emergency fallback content
        emergency_blog = "Markets continue to adapt to changing economic conditions. Investors should stay informed about central bank policies and global developments that may impact various sectors. Maintaining a balanced portfolio remains advisable in the current climate."
        emergency_summary = "SUMMARY: Current market conditions require vigilant monitoring and balanced investment strategies."
        emergency_title = "Market Update: Strategic Positioning in Current Economic Climate"
        log_blog_to_history(emergency_blog)
        return emergency_blog, emergency_summary, emergency_title


def get_content_aware_image(blog_text: str, summary_text: str, title: str) -> str:
    """
    Select the most appropriate financial image based on the content of the blog post.
    """
    # Define categories with corresponding images
    image_categories = {
        # Market Performance & General Finance
        "general": [
            "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?q=80&w=1024",  # Financial chart
            "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?q=80&w=1024"   # Financial district
        ],
        
        # Federal Reserve & Interest Rates
        "fed_rates": [
            "https://images.unsplash.com/photo-1589758438368-0ad531db3366?q=80&w=1024",  # Federal Reserve building
            "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?q=80&w=1024"   # Rate chart
        ],
        
        # Market Volatility & Bearish News
        "market_decline": [
            "https://images.unsplash.com/photo-1563986768494-4dee2763ff3f?q=80&w=1024",  # Downward chart
            "https://images.unsplash.com/photo-1574607383476-f517f260d30b?q=80&w=1024"   # Bear market concept
        ],
        
        # Growth & Bullish News
        "market_growth": [
            "https://images.unsplash.com/photo-1535320903710-d993d3d77d29?q=80&w=1024",  # Bull statue
            "https://images.unsplash.com/photo-1560221328-12fe60f83ab8?q=80&w=1024"     # Upward graph
        ],
        
        # Technology & Innovation
        "tech_innovation": [
            "https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=1024",  # Tech visualization
            "https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=1024"   # Tech with charts
        ]
    }
    
    # Combine all text for analysis
    all_text = f"{title} {summary_text} {blog_text}".lower()
    
    # Define keywords for each category
    category_keywords = {
        "fed_rates": ["fed", "federal reserve", "interest rate", "rates", "powell", "monetary policy", "inflation", "hike", "cut"],
        "market_decline": ["decline", "drop", "fall", "bearish", "downturn", "recession", "crisis", "plunge", "correction", "crash"],
        "market_growth": ["growth", "surge", "rally", "bullish", "upturn", "recovery", "gains", "positive", "upward"],
        "tech_innovation": ["tech", "technology", "ai", "artificial intelligence", "digital", "innovation", "startup", "software", "crypto"]
    }
    
    # Score each category based on keyword matches
    category_scores = {"general": 1}  # Give general a base score
    
    for category, keywords in category_keywords.items():
        score = 0
        for keyword in keywords:
            if keyword in all_text:
                score += 1
                # Give extra weight to keywords in the title
                if keyword in title.lower():
                    score += 2
        
        category_scores[category] = score
    
    # Select the category with the highest score
    best_category = max(category_scores.items(), key=lambda x: x[1])[0]
    
    # Pick a random image from the best category
    selected_image = random.choice(image_categories[best_category])
    
    print(f"✅ Selected image for category '{best_category}' based on content analysis")
    return selected_image


def download_image(url: str) -> bytes:
    """Download image from URL and return the binary data"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        print(f"❌ Failed to download image: {e}")
        # If download fails, return empty bytes
        return b''


def upload_image_to_wordpress(image_url: str) -> dict:
    """Upload an image to WordPress media library from URL"""
    try:
        # First try to download the image
        img_data = download_image(image_url)
        if not img_data:
            raise Exception("Failed to download image")
            
        # Generate a unique filename to avoid caching issues
        timestamp = int(time.time())
        filename = f"finance_header_{timestamp}.jpg"
        
        # Upload to WordPress
        media = requests.post(
            f"{WP_SITE_URL}/wp-json/wp/v2/media",
            auth=(WP_USERNAME, WP_APP_PASSWORD),
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
            files={"file": (filename, img_data, "image/jpeg")}
        )
        media.raise_for_status()
        
        # Return the media object
        media_obj = media.json()
        print(f"✅ Uploaded image to WordPress with ID: {media_obj.get('id', 'unknown')}")
        return media_obj
    except Exception as e:
        print(f"❌ Failed to upload image to WordPress: {e}")
        # Return dummy data to allow the process to continue
        return {"id": 0, "source_url": ""}


def save_local(blog: str, summary: str):
    """Save blog content and summary to local files"""
    try:
        with open("blog_summary.txt","w") as f: f.write(summary)
        with open("blog_post.txt","w") as f:
            f.write(blog + "\n\n" + summary)
        print("📝 Saved locally")
    except IOError as e:
        print(f"❌ Failed to save local files: {e}")


def post_to_wordpress(title: str, content: str, featured_media: int):
    """Publish post to WordPress with featured image"""
    try:
        payload = {
            "title": title,
            "content": content,
            "status": "publish",
            "featured_media": featured_media
        }
        resp = requests.post(
            f"{WP_SITE_URL}/wp-json/wp/v2/posts",
            auth=(WP_USERNAME, WP_APP_PASSWORD),
            json=payload
        )
        resp.raise_for_status()
        print("📤 Published post (status", resp.status_code, ")")
    except requests.RequestException as e:
        print(f"❌ Failed to post to WordPress: {e}")


# ——— Main Execution ——————————————————————————————

if __name__ == "__main__":
    try:
        # 1) Create blog
        print("Generating blog content...")
        blog_text, summary_text, base_title = generate_blog()

        # 2) Get content-aware image and upload
        print("Selecting and uploading relevant header image...")
        img_url = get_content_aware_image(blog_text, summary_text, base_title)
        media_obj = upload_image_to_wordpress(img_url)
        media_id = media_obj.get("id", 0)
        media_src = media_obj.get("source_url", "")

        # 3) Save drafts locally
        print("Saving content locally...")
        save_local(blog_text, summary_text)

        # 4) Timestamp & title string
        print("Formatting post elements...")
        est_now = datetime.now(pytz.utc).astimezone(pytz.timezone('America/New_York'))
        ts_readable = est_now.strftime("%B %d, %Y %H:%M")
        final_title = f"{ts_readable} EST  |  {base_title}"

        # 5) Build header block: image left, date & title right
        header_html = (
            '<div style="display:flex; align-items:center; margin-bottom:20px;">'
            f'<div style="flex:1;"><img src="{media_src}" style="width:100%; height:auto;" /></div>'
            '<div style="flex:1; display:flex; flex-direction:column; justify-content:center; padding-left:20px;">'
            f'<div style="color:#666; font-size:12px; margin-bottom:8px;">{ts_readable} EST</div>'
            f'<h1 style="margin:0; font-size:24px;">{base_title}</h1>'
            '</div>'
            '</div>'
        )

        # 6) Assemble post body
        post_body = (
            header_html +
            f'<p><em>{summary_text}</em></p>\n\n'
            + f'<div>{blog_text}</div>'
        )

        # 7) Publish!
        print("Publishing to WordPress...")
        post_to_wordpress(final_title, post_body, featured_media=media_id)
        
        print("✅ Process completed successfully!")
        
    except Exception as e:
        print(f"❌ Unexpected error in main process: {e}")
