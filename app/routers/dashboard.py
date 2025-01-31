import json
import logging
import os
import shutil
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User, Content, TikTokAccount
from app.utils.jwt import verify_access_token
from app.utils.random_profile_generator import generate_random_profile_photo
from datetime import datetime
from fastapi import Query
from datetime import datetime


router = APIRouter()


router.mount("/static", StaticFiles(directory=os.path.join(os.getcwd(), "static")), name="static")
router.mount("/uploads", StaticFiles(directory=os.path.join(os.getcwd(), "uploads")), name="uploads")

templates = Jinja2Templates(directory="templates")


PROFILE_PHOTO_DIR = os.path.join(os.getcwd(), "static", "profile_photos")

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, token: str = None, db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")

    try:
        # Decode the JWT token to get the email (or other user info)
        user_data = verify_access_token(token)

        # Extract email from token
        email = user_data.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Token is invalid or missing email")
        
        if "email" not in request.session:
            request.session["email"] = email

        # Retrieve the user profile from the database using the email
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Generate or fetch profile photo URL
        profile_photo_url = user.profile_photo_url if user.profile_photo_url else "default_profile_photo_url.png"
        
        username = user.full_name  # Assuming `full_name` is the column for the username

        # Fetch TikTok info if linked
        tiktok_account = db.query(TikTokAccount).filter(TikTokAccount.user_id == user.id).first()
        tiktok_username = tiktok_account.username if tiktok_account else None
        tiktok_profile_picture = tiktok_account.profile_picture if tiktok_account else None
        
        print(f"tiktok_username: {tiktok_username}")
        print(f"tiktok_profile_picture: {tiktok_profile_picture}")

        # If user is linked to TikTok, show /me page with TikTok info
        if tiktok_account:
            return templates.TemplateResponse("dashboard.html", {
                "request": request,
                "username": username,
                "email": email,
                "profile_photo_url": profile_photo_url,
                "tiktok_username": tiktok_account.username,
                "tiktok_profile_picture": tiktok_account.profile_picture,
            })
        
        # Otherwise, show main dashboard and offer TikTok login
        return templates.TemplateResponse("schedule.html", {
                "request": request,
                "username": username,
                "email": email,
                "profile_photo_url": profile_photo_url,
            })

    except HTTPException:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


    
@router.get("/{section}", response_class=HTMLResponse)
async def load_section(request: Request, section: str):
    """
    Load dynamic content based on the section parameter.
    """
    if section == "schedule":
        return templates.TemplateResponse("schedule.html", {"request": request})
    elif section == "calendar":
        # Render the calendar section (replace with actual calendar logic)
        return templates.TemplateResponse("calendar.html", {"request": request })
    else:
        return HTMLResponse(content="Section Not Found", status_code=404)
    
    
@router.post("/upload-profile-photo")
async def upload_profile_photo(
    email: str = Form(...), 
    profile_photo: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    try:
        # Generate a unique filename for the uploaded profile photo
        file_extension = profile_photo.filename.split('.')[-1]
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        new_filename = f"profile_{timestamp}.{file_extension}"
        file_path = os.path.join(PROFILE_PHOTO_DIR, new_filename)

        # Save the uploaded photo to the specified directory
        with open(file_path, "wb") as f:
            shutil.copyfileobj(profile_photo.file, f)

        # Fetch the user from the database using the email
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Update the user's profile photo URL in the database
        user.profile_photo_url = f"/static/profile_photos/{new_filename}"
        db.commit()

        # Return a success response with the new profile photo URL
        return JSONResponse(content={"success": True, "newPhotoUrl": f"/static/profile_photos/{new_filename}"})

    except Exception as e:
        # Log the error and raise an HTTPException
        logging.error(f"Error uploading profile photo: {e}")
        raise HTTPException(status_code=500, detail="Error uploading profile photo")




@router.post("/api/content-data/")
async def create_content_data(
    title: str = Form(...),
    description: str = Form(...),
    tags: str = Form(...),
    end_time: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),  # Use dependency to get the DB session
):
    try:
        # Convert the string end time into a datetime object
        end_datetime = datetime.fromisoformat(end_time).replace(tzinfo=None)  # Make naive

        # Save the image file to a directory
        file_location = f"uploads/{image.filename}"
        with open(file_location, "wb") as f:
            f.write(await image.read())

        # Assuming user is logged in, fetch the user_id
        user_id = 1  # Replace this with the actual logged-in user ID logic
        
        # Create content instance and insert into the database
        new_content = Content(
            user_id=user_id,
            platform="tiktok",  # or another platform if necessary
            media_url=file_location,  # Save the image/video path in the media_url
            title=title,
            description=description,
            tags=tags,
            scheduled_time=end_datetime,
        )

        # Add content to the database and commit
        db.add(new_content)
        db.commit()

        return {"status": "success", "message": "Content data saved successfully"}

    except Exception as e:
        print(f"Error: {str(e)}")  # Log the full error
        raise HTTPException(status_code=500, detail=f"Error saving content data: {str(e)}")



@router.get("/api/events")
async def get_events(start: str = Query(None), end: str = Query(None)):
    try:
        # Load events from the file
        events_file_path = "events.json"

        if not os.path.exists(events_file_path):
            raise HTTPException(status_code=404, detail="No events found")

        with open(events_file_path, "r") as event_file:
            events = json.load(event_file)

        # Parse and filter events based on the `start` and `end` parameters
        if start and end:
            start_date = datetime.fromisoformat(start)
            end_date = datetime.fromisoformat(end)
            events = [
                event for event in events
                if datetime.fromisoformat(event["end"]) >= start_date
                and datetime.fromisoformat(event["end"]) <= end_date
            ]

        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not load events: {str(e)}")
