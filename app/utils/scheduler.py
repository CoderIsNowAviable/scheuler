from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import logging
from fastapi import HTTPException, Request
import httpx
from sqlalchemy.orm import Session
from app.models.user import Content

# Initialize the scheduler
scheduler = BackgroundScheduler()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



async def post_content_to_tiktok(request: Request, content_id: int, db: Session):
    # Step 1: Fetch content data from the database
    content = db.query(Content).filter(Content.id == content_id).first()

    if content:
        tiktok_session = request.session.get("tiktok_session")
        access_token = tiktok_session.get("access_token")
        
        if not access_token:
            raise HTTPException(status_code=401, detail="User is not authenticated with TikTok.")
        
        # Step 2: Post content (image/video) to TikTok using the API
        url = "https://open-api.tiktok.com/v1/video/publish/"
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
