from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import logging
import httpx
import os
from sqlalchemy.orm import Session
from asgiref.sync import async_to_sync
from app.models.user import Content, TikTokAccount
from app.core.database import SessionLocal  # Import database session factory

# Initialize the scheduler
scheduler = BackgroundScheduler()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def post_content_to_tiktok(content_id: int):
    """Function to post scheduled content to TikTok"""
    logger.info(f"Starting TikTok post process for Content ID {content_id} at {datetime.utcnow()}")

    db = SessionLocal()  # Manually create a database session
    try:
        # Fetch content data
        content = db.query(Content).filter(Content.id == content_id).first()
        if not content:
            logger.error(f"Content ID {content_id} not found in the database.")
            return

        # Retrieve TikTok access token
        user_tiktok_data = db.query(TikTokAccount).filter(TikTokAccount.user_id == content.user_id).first()
        if not user_tiktok_data or not user_tiktok_data.access_token:
            logger.error(f"User {content.user_id} is not authenticated with TikTok.")
            return

        access_token = user_tiktok_data.access_token

        # Check if media file exists
        media_path = os.path.abspath(os.path.join(os.getcwd(), "static", content.media_url.lstrip("/")))
        if not os.path.exists(media_path):
            logger.error(f"Media file not found: {media_path}")
            return

        # Log media and access token info (mask token for security)
        logger.info(f"Posting Content ID {content_id}: {content.title}, Media: {content.media_url}")
        
        # Post to TikTok
        url = "https://open.tiktokapis.com/v2/post/publish/creator_info/query/"
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        data = {"video_url": content.media_url, "title": content.title}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=headers)

        if response.status_code == 200:
            logger.info(f"Content ID {content_id} successfully posted to TikTok at {datetime.utcnow()}.")
        else:
            logger.error(f"Failed to post content ID {content_id}. TikTok Response: {response.json()}")

    except Exception as e:
        logger.exception(f"Error posting content ID {content_id} to TikTok: {str(e)}")
    finally:
        db.close()  # Close the session
        logger.info(f"Database session closed for Content ID {content_id}")

# Wrapper to make async function synchronous for APScheduler
def sync_post_content_to_tiktok(content_id: int):
    logger.info(f"Executing scheduled TikTok post for Content ID {content_id} at {datetime.utcnow()}")
    async_to_sync(post_content_to_tiktok)(content_id)

# Function to start the scheduler
def start_scheduler():
    """Start the APScheduler background scheduler."""
    logger.info("Starting APScheduler...")
    scheduler.start()

# Function to schedule content posting
def schedule_content_post(content_id: int, end_time: datetime):
    """Schedules a job to post content at the specified end_time."""
    try:
        scheduler.add_job(
            sync_post_content_to_tiktok,  # Wrapped function to make it sync
            'date',  # Runs at a specific time
            run_date=end_time,
            args=[content_id],  # Pass content_id
            id=f"content_post_{content_id}",  # Unique job ID
            misfire_grace_time=3600,  # Allow retry if missed
        )
        logger.info(f"Content ID {content_id} scheduled for {end_time}.")
    except Exception as e:
        logger.error(f"Error scheduling content ID {content_id}: {str(e)}")
