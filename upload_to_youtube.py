import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# SETTINGS
VIDEO_FILE = "video_output.mp4"
TITLE = "Today's AI-Generated Market Recap #Shorts"
DESCRIPTION = "Get a quick overview of today’s market trends, powered by AI. #Shorts"
CATEGORY_ID = "25"  # News & Politics
PRIVACY = "public"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def upload_video():
    # Step 1: OAuth login
    flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
    credentials = flow.run_console()

    # Step 2: Build YouTube API client
    youtube = build("youtube", "v3", credentials=credentials)

    # Step 3: Prepare video metadata
    body = {
        "snippet": {
            "title": TITLE,
            "description": DESCRIPTION,
            "tags": ["finance", "stocks", "Shorts", "ai", "market"],
            "categoryId": CATEGORY_ID
        },
        "status": {
            "privacyStatus": PRIVACY
        }
    }

    # Step 4: Upload video file
    media = MediaFileUpload(VIDEO_FILE, mimetype="video/mp4", resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    print("📤 Uploading to YouTube...")
    response = request.execute()

    print("✅ Uploaded!")
    print("🔗 Video URL: https://youtube.com/watch?v=" + response["id"])

if __name__ == "__main__":
    upload_video()
