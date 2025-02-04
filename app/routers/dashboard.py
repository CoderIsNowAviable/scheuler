import logging
import os
import shutil
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import urllib.parse
from app.core.database import get_db
from app.models.user import User, Content, TikTokAccount
from app.utils.jwt import get_current_user, get_email_from_Ctoken, verify_access_token
from app.utils.random_profile_generator import generate_random_profile_photo
from datetime import datetime, timedelta
from fastapi import Query
from datetime import datetime
from app.models.user import User, Content, TikTokAccount
from app.utils.GetTiktok import get_tiktok_info
from app.utils.scheduler import schedule_content_post

router = APIRouter()


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
        return RedirectResponse(url="/register?form=signin", status_code=302)

    # Fetch the user from the database
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        # If user does not exist, clear session and redirect to login
        request.session.clear()
        return RedirectResponse(url="/register?form=signin", status_code=302)

    # Check if TikTok is linked to the user
    tiktok_account = db.query(TikTokAccount).filter(TikTokAccount.user_id == user.id).first()

    # Prepare user data for the template
    user_data = {
        "user_id": user.id, 
        "username": user.full_name,  # Assuming `full_name` is the correct field
        "email": user.email,
    }

    # Check if the user has a profile photo
    if user.profile_photo_url:
        # If the user has a profile picture, use that
        user_data["profile_photo_url"] = user.profile_photo_url
    else:
        # If not, generate a random profile picture
        user_data["profile_photo_url"] = generate_random_profile_photo(user,db)  # Call the function to generate

    # Add TikTok details to user_data if TikTok account is linked
    if tiktok_account:
        user_data["tiktok_username"] = tiktok_account.username
        user_data["tiktok_profile_picture"] = tiktok_account.profile_picture

    # Check if TikTok account is linked to the user
    if tiktok_account:
        # If TikTok account is linked, redirect to /dashboard/me
        return RedirectResponse(url="/dashboard/me", status_code=302)

    # If TikTok is not linked, render dashboard with user data
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
        return RedirectResponse(url="/register?form=signin", status_code=302)

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
    return templates.TemplateResponse("dashboard.html", {"request": request, **user_profile_data})



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
        return RedirectResponse(url="/register?form=signin", status_code=302)

    # Fetch the user from the database
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        # If user not found, clear session and redirect
        request.session.clear()
        raise HTTPException(status_code=401, detail="Invalid session. Please log in again.")
    tiktok_account = db.query(TikTokAccount).filter(TikTokAccount.user_id == user.id).first()
    tiktok_username = tiktok_account.username if tiktok_account else None
    tiktok_profile_picture = tiktok_account.profile_picture if tiktok_account else None
    print("tiktok_username",tiktok_username)
    print("tiktok_profile_picture",tiktok_profile_picture)
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
        # Ensure `uploads_dir` is defined inside static
        uploads_dir = os.path.abspath(os.path.join(os.getcwd(), "static", "uploads"))
        if not os.path.exists(uploads_dir):
            return {"status": "error", "message": "Uploads directory does not exist"}

        # Step 1: Try to retrieve TikTok session from the session
        tiktok_session = request.session.get("tiktok_session")
        user_id = None

        if tiktok_session:
            user_id = tiktok_session.get("user_id")

        # Step 2: If no session found, fetch TikTok info from the database
        if not user_id:
            tiktok_info = await get_tiktok_info(request, db)
            user_id = tiktok_info.get("user_id")  # Retrieve user_id from the function

        # Step 3: If still no user_id, return login prompt
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated with TikTok. Please log in to TikTok.")

        # Convert the string end time into a datetime object
        end_datetime = datetime.fromisoformat(end_time).replace(tzinfo=None)  # Make naive

        # Ensure the folder exists
        os.makedirs(uploads_dir, exist_ok=True)

        # Save the image file to the uploads directory inside static
        encoded_filename = urllib.parse.quote(image.filename)
        file_location = os.path.join(uploads_dir, encoded_filename)
        media_url = "/static/uploads/" + encoded_filename

        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        # Create content instance and insert into the database
        new_content = Content(
            user_id=user_id,  # Use the dynamically fetched user_id
            platform="tiktok",  # or another platform if necessary
            media_url=media_url,  # Save the image/video path in the media_url
            title=title,
            description=description,
            tags=tags,
            scheduled_time=end_datetime,
        )

        # Add content to the database and commit
        db.add(new_content)
        db.commit()
        # Schedule content posting
        schedule_content_post(new_content.id, end_datetime)
        return {"status": "success", "message": "Content data saved successfully"}

    except Exception as e:
        print(f"Error: {str(e)}")  # Log the full error
        raise HTTPException(status_code=500, detail=f"Error saving content data: {str(e)}")



@router.get("/api/events")
async def get_events(request: Request, db: Session = Depends(get_db)):
    """
    Fetch events (scheduled content) for the logged-in user only.
    """
    user_id = request.session.get("user_id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Fetch user events (scheduled content) from the Content table
    events = db.query(Content).filter(Content.user_id == user_id, Content.scheduled_time >= datetime.utcnow()).all()
    
        # Return events data, filter or format as needed
    return [
        {
            "title": event.title,
            "start": event.scheduled_time.isoformat(),  # Assuming event has a scheduled_time field
            "end": event.scheduled_time.isoformat(),  # Can adjust this based on your event duration logic
            "description": event.description,
            "media_url": event.media_url,  # You can add media URL if required
        }
        for event in events
    ]

@router.get("/api/tiktok-profile",)
async def get_tiktok_profile(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint to fetch the logged-in user's TikTok profile data.
    This endpoint is called dynamically by JavaScript in the SPA.
    """
    user_id = request.session.get("user_id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Fetch the user from the database
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid session. Please log in again.")

    # Fetch TikTok account linked to the user
    tiktok_account = db.query(TikTokAccount).filter(TikTokAccount.user_id == user.id).first()

    if not tiktok_account:
        return {"tiktok_username": None, "tiktok_profile_picture": None}

    return {
        "tiktok_username": tiktok_account.username,
        "tiktok_profile_picture": tiktok_account.profile_picture
    }
