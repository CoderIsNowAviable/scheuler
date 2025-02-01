import json
import logging
import os
import shutil
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile,status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User, Content, TikTokAccount
from app.utils.jwt import get_current_user, get_email_from_Ctoken, verify_access_token
from app.utils.random_profile_generator import generate_random_profile_photo
from datetime import datetime, timedelta
from fastapi import Query
from datetime import datetime
from app.models.user import User, Content, TikTokAccount


router = APIRouter()


router.mount("/static", StaticFiles(directory=os.path.join(os.getcwd(), "static")), name="static")
router.mount("/uploads", StaticFiles(directory=os.path.join(os.getcwd(), "uploads")), name="uploads")

templates = Jinja2Templates(directory="templates")


PROFILE_PHOTO_DIR = os.path.join(os.getcwd(), "static", "profile_photos")



@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    """
    Dashboard page that isolates user data based on session authentication.
    Ensures only the logged-in user's data is retrieved.
    """

    # Retrieve the user ID from the session
    user_id = request.session.get("user_id")

    if not user_id:
        # If no user ID in session, redirect to login
        return RedirectResponse(url="/login", status_code=302)

    # Fetch the user from the database
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        # If user does not exist, clear session and redirect to login
        request.session.clear()
        raise HTTPException(status_code=401, detail="Invalid session. Please log in again.")

    # Check if TikTok is linked to the user
    tiktok_account = db.query(TikTokAccount).filter(TikTokAccount.user_id == user.id).first()

    # Prepare user data for the template
    user_data = {
        "user_id": user.id, 
        "username": user.full_name,  # Assuming `full_name` is the correct field
        "email": user.email,
        "profile_photo_url": user.profile_photo_url if user.profile_photo_url else "default_profile_photo_url.png",
        "tiktok_username": tiktok_account.username if tiktok_account else None,
        "tiktok_profile_picture": tiktok_account.profile_picture if tiktok_account else None,
    }

    if tiktok_account:
        # If TikTok account is linked, redirect to /dashboard/me
        return RedirectResponse(url="/dashboard/me", status_code=302)

    # If TikTok is not linked, render dashboard without TikTok info
    return templates.TemplateResponse("dashboard.html", {"request": request, **user_data})


@router.get("/me", response_class=HTMLResponse)
async def get_user_profile(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint to get the logged-in user's profile information and verify their TikTok account.
    Only allows access to users with a linked TikTok account.
    """
    
    # Retrieve the user ID from the session
    user_id = request.session.get("user_id")

    if not user_id:
        # If no user ID in session, redirect to login
        return RedirectResponse(url="/login", status_code=302)

    # Fetch the user from the database
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        # If user does not exist, clear session and redirect to login
        request.session.clear()
        raise HTTPException(status_code=401, detail="Invalid session. Please log in again.")

    # Fetch TikTok info linked to the logged-in user (if exists)
    tiktok_account = db.query(TikTokAccount).filter(TikTokAccount.user_id == user.id).first()

    # If no TikTok account is linked, redirect to the dashboard or another page
    if not tiktok_account:
        return RedirectResponse(url="/dashboard", status_code=302)

    # If TikTok account exists, prepare user profile data
    tiktok_username = tiktok_account.username if tiktok_account else None
    tiktok_profile_picture = tiktok_account.profile_picture if tiktok_account else None

    # Prepare user profile data, including TikTok information (if available)
    user_profile_data = {
        "user_id": user.id,
        "username": user.full_name,  # Assuming `full_name` is the correct field
        "email": user.email,
        "profile_photo_url": user.profile_photo_url or "default_profile_photo_url.png",
        "tiktok_username": tiktok_username,
        "tiktok_profile_picture": tiktok_profile_picture,
        "tiktok_account_exists": bool(tiktok_account),  # Add a flag indicating if TikTok account is linked
    }
    # Render the user profile template with the data
    return templates.TemplateResponse("profile.html", {"request": request, **user_profile_data})



@router.get("/me/{section}", response_class=HTMLResponse)
async def load_section(request: Request, section: str, db: Session = Depends(get_db)):
    """
    Load dynamic content based on the section parameter.
    Ensures that only authenticated users can access their own data.
    """

    # Retrieve the user ID from session
    user_id = request.session.get("user_id")

    if not user_id:
        # If no user ID in session, redirect to login
        return RedirectResponse(url="/login", status_code=302)

    # Fetch the user from the database
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        # If user not found, clear session and redirect
        request.session.clear()
        raise HTTPException(status_code=401, detail="Invalid session. Please log in again.")
    tiktok_account = db.query(TikTokAccount).filter(TikTokAccount.user_id == user.id).first()
    tiktok_username = tiktok_account.username if tiktok_account else None
    tiktok_profile_picture = tiktok_account.profile_picture if tiktok_account else None
    # Prepare user-specific data
    user_data = {
        "userId": user.id,
        "username": user.full_name,  # Assuming `full_name` is correct
        "profilePhotoUrl": user.profile_photo_url or "default_profile_photo_url.png",
        "email": user.email,
        "tiktokUsername": tiktok_username,
        "tiktokProfilePicture": tiktok_profile_picture,
    }

    # Render the requested section
    if section == "schedule":
        return templates.TemplateResponse("schedule.html", {"request": request, "user": user_data})
    
    elif section == "calendar":
        return templates.TemplateResponse("calendar.html", {"request": request, "user": user_data})
    
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
    request: Request,  # Get the request object to access the session
    title: str = Form(...),
    description: str = Form(...),
    tags: str = Form(...),
    end_time: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    try:
        # Retrieve the TikTok session from the session
        tiktok_session = request.session.get("tiktok_session")
        
        if not tiktok_session:
            raise HTTPException(status_code=401, detail="User not authenticated with TikTok")
        
        # Retrieve the email or open_id from the session
        user_email = tiktok_session.get("email")
        
        if not user_email:
            raise HTTPException(status_code=401, detail="TikTok email not found in session")
        
        # Retrieve the user_id from the database based on the email
        user = db.query(User).filter(User.email == user_email).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Extract the user_id
        user_id = user.id

        # Convert the string end time into a datetime object
        end_datetime = datetime.fromisoformat(end_time).replace(tzinfo=None)  # Make naive

        # Save the image file to a directory
        file_location = f"uploads/{image.filename}"
        with open(file_location, "wb") as f:
            f.write(await image.read())

        # Create content instance and insert into the database
        new_content = Content(
            user_id=user_id,  # Use the dynamically fetched user_id
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
async def get_events(start: str = Query(None), end: str = Query(None), db: Session = Depends(get_db)):
    try:
        # Parse and filter events based on the `start` and `end` parameters
        if start and end:
            start_date = datetime.fromisoformat(start)
            end_date = datetime.fromisoformat(end)

            # Query contents from the database within the given date range
            events = db.query(Content).filter(
                Content.scheduled_time >= start_date,
                Content.scheduled_time <= end_date
            ).all()

        else:
            # If no date range is provided, retrieve all content events
            events = db.query(Content).all()

        # Format the events for the calendar
        calendar_events = [
            {
                "title": event.title,
                "start": (event.scheduled_time - timedelta(minutes=1)).isoformat(),  # Subtract 1 minute for start
                "end": event.scheduled_time.isoformat(),  # Use scheduled_time as end time
                "description": event.description,
                "media_url": event.media_url,
            }
            for event in events
        ]

        return calendar_events

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not load events: {str(e)}")


@router.get("/api/tiktok-profile")
async def get_tiktok_profile(request: Request, db: Session = Depends(get_db)):
    # Retrieve the tiktok session from the request session
    tiktok_session = request.session.get("tiktok_session")
    if not tiktok_session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    # Extract open_id and access_token from the session
    openid = tiktok_session.get("open_id")
    access_token = tiktok_session.get("access_token")

    if not openid or not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session data")

    # Query the TikTok account from the database
    tiktok_account = db.query(TikTokAccount).filter(TikTokAccount.openid == openid).first()

    if not tiktok_account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="TikTok account not found")

    # Return the TikTok account details
    return JSONResponse(content={
        "tiktok_username": tiktok_account.username,
        "tiktok_profile_picture": tiktok_account.profile_picture
    }, status_code=200)