import os
import requests
from dotenv import load_dotenv

# Load .env
load_dotenv()

WP_USERNAME = os.getenv("WP_USERNAME")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")
WP_SITE_URL = os.getenv("WP_SITE_URL")

file_path = "voiceover.mp3"
file_name = os.path.basename(file_path)
media_url = f"{WP_SITE_URL}/wp-json/wp/v2/media"

headers = {
    "Content-Disposition": f"attachment; filename={file_name}",
    "Content-Type": "audio/mpeg"
}

# Upload
with open(file_path, 'rb') as f:
    response = requests.post(
        media_url,
        headers=headers,
        data=f,
        auth=(WP_USERNAME, WP_APP_PASSWORD)
    )

if response.status_code in [200, 201]:
    media = response.json()
    print("✅ Audio uploaded!")
    print("🔗 URL:", media["source_url"])
else:
    print("❌ Upload failed:", response.status_code)
    print(response.text)
