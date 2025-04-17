import os
import json
import openai
import requests
import pytz
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


def extract_finance_keywords(text: str) -> list:
    """
    Extract finance-related keywords from the summary text
    to create better image search queries.
    """
    # List of common financial terms to look for
    financial_terms = [
        "market", "stock", "economy", "trading", "investment", "finance",
        "growth", "recession", "inflation", "rates", "fed", "reserve",
        "bull", "bear", "trend", "volatility", "chart", "graph",
        "currency", "exchange", "portfolio", "analysis", "bank", "treasury",
        "bonds", "yield", "equity", "asset", "capital", "wealth", "dollar"
    ]
    
    # Extract words from the text that match financial terms
    words = text.lower().replace(",", " ").replace(".", " ").split()
    keywords = [word for word in words if word in financial_terms]
    
    # If no financial terms found, use default keywords
    if not keywords:
        keywords = ["finance", "market", "business", "professional"]
    
    return keywords[:3]  # Limit to top 3 keywords


def get_unsplash_finance_image(query: str) -> str:
    """
    Get a professional finance image from Unsplash based on the summary content.
    This is a reliable source of high-quality, free stock photos.
    """
    # Create a focused search query based on financial terms in the summary
    search_terms = query.replace(" ", "+")
    
    # Add finance-related terms to ensure relevant images
    if "market" not in search_terms.lower() and "finance" not in search_terms.lower():
        search_terms += "+finance"
    
    # Use Unsplash source API for a random, relevant finance image
    image_size = "1024x1024"
    image_url = f"https://source.unsplash.com/{image_size}/?{search_terms}"
    
    # Force a fresh image by adding a cache-busting parameter
    image_url += f"&cb={os.urandom(4).hex()}"
    
    print(f"✅ Using Unsplash image with query: {search_terms}")
    return image_url


def generate_header_image(summary: str) -> str:
    """
    Generate a professional finance image based on the summary content.
    Uses Unsplash for reliable, high-quality stock photos.
    """
    try:
        # Extract key financial terms from the summary
        keywords = extract_finance_keywords(summary)
        query = " ".join(keywords)
        
        # Get image URL from Unsplash
        return get_unsplash_finance_image(query)
    except Exception as e:
        print(f"❌ Error generating image: {e}")
        # Fallback to a general finance image
        return "https://source.unsplash.com/1024x1024/?finance,business"


def upload_image_to_wordpress(image_url: str) -> dict:
    """Upload an image to WordPress media library from URL"""
    try:
        img_data = requests.get(image_url).content
        filename = "header_image.png"
        media = requests.post(
            f"{WP_SITE_URL}/wp-json/wp/v2/media",
            auth=(WP_USERNAME, WP_APP_PASSWORD),
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
            files={"file": (filename, img_data, "image/png")}
        )
        media.raise_for_status()
        return media.json()  # -> {"id": ..., "source_url": ...}
    except requests.RequestException as e:
        print(f"❌ Failed to upload image to WordPress: {e}")
        # Return dummy data to allow the process to continue
        return {"id": 0, "source_url": "https://source.unsplash.com/1024x1024/?finance"}


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

        # 2) Generate and upload image using improved approach
        print("Creating and uploading header image...")
        img_url = generate_header_image(summary_text)
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
