from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import logging
from fastapi import HTTPException, Request
import httpx
import os
from sqlalchemy.orm import Session
from app.models.user import Content
from asgiref.sync import async_to_sync


# Initialize the scheduler
scheduler = BackgroundScheduler()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def post_content_to_tiktok(request: Request, content_id: int, db: Session):
    # Step 1: Fetch content data from the database
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        logger.error(f"Content ID {content_id} not found in the database.")
        return
    
    tiktok_session = request.session.get("tiktok_session")
    if not tiktok_session:
        logger.error("TikTok session not found.")
        return
    
    access_token = tiktok_session.get("access_token")
    if not access_token:
        logger.error("User is not authenticated with TikTok.")
        return
    
    # Ensure media file exists before posting
    media_path = os.path.abspath(os.path.join(os.getcwd(), "static", content.media_url.lstrip("/")))
    if not os.path.exists(media_path):
        logger.error(f"Media file not found: {media_path}")
        return
    
    # Step 2: Post content (image/video) to TikTok using the API
    url = "https://open.tiktokapis.com/v2/post/publish/creator_info/query/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    data = {
        "video_url": content.media_url,  # Assume you store the URL of the video or image in the database
        "title": content.title,
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data, headers=headers)

    if response.status_code == 200:
        logger.info(f"Content with ID {content_id} successfully posted to TikTok.")
    else:
        logger.error(f"Failed to post content to TikTok: {response.json()}")

# Function to start the scheduler
def start_scheduler():
    """Start the APScheduler background scheduler."""
    scheduler.start()

# Function to schedule content posting
def schedule_content_post(content_id: int, end_time: datetime, db: Session):
    try:
        def run_post_content():
            async_to_sync(post_content_to_tiktok)(None, content_id, db)
        # Add a job to the scheduler to post content at the `end_time`
        scheduler.add_job(
            post_content_to_tiktok,  # The function that posts content
            'date',  # Trigger once when the exact time arrives
            run_date=end_time,  # The time when the job should run
            args=[content_id, db],  # Pass content_id and db to the function
            id=f"content_post_{content_id}",  # Unique job ID
            misfire_grace_time=3600,  # Allow retry in case of error
        )
        logger.info(f"Content ID {content_id} scheduled for {end_time}.")
    except Exception as e:
        logger.error(f"Error scheduling content: {str(e)}")
