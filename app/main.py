from datetime import datetime
import json
import logging
import shutil
from fastapi import Cookie, Depends, FastAPI, Form, HTTPException, Request, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.core.database import engine, Base, SessionLocal,get_db
from app.models.user import User
from sqlalchemy.orm import Session
from app.routers.user import router as user_router
from app.routers.auth import router as auth_router
from app.routers.pages import router as pages_router
from fastapi.middleware.cors import CORSMiddleware
from urllib.parse import quote
import os
import requests
from dotenv import load_dotenv
from app.utils.random_profile_generator import generate_random_profile_photo

from app.utils.jwt import get_email_from_token, verify_access_token

# Initialize database models
Base.metadata.create_all(bind=engine)

# Load environment variables
load_dotenv()

CLIENT_KEY = os.getenv("CLIENT_KEY")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

# Initialize FastAPI app
app = FastAPI()

# Dependency to manage the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Encoding the redirect URI
encoded_redirect_uri = quote(REDIRECT_URI, safe="")

# Middleware setup for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",
        "http://127.0.0.1:8000",  # Local development
        "http://localhost:8000",  # Local development
        "https://scheduler-9v36.onrender.com",
        "https://scheduler-9v36.onrender.com/terms-and-conditions",
        "https://scheduler-9v36.onrender.com/privacy-policy"
        # Production domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
PROFILE_PHOTO_DIR = "static/profile_photos"
# Include routers
app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(pages_router, prefix="/pages", tags=["pages"])
os.makedirs("uploads", exist_ok=True)

@app.on_event("startup")
async def startup_event():
    print(f"CLIENT_KEY: {CLIENT_KEY}")
    print(f"REDIRECT_URI: {REDIRECT_URI}")
    

    
# Serve the HTML verification file for domain/app verification
@app.get("/googleb524bf271b1d073d.html")  # Change the filename to your actual file
async def serve_verification_file():
    file_path = "static/googleb524bf271b1d073d.html"  # Ensure this file is placed in the `static` folder
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "File not found"}




@app.get("/tiktokBqCp0CjXfV1QtT9rl09qvRrnXgzDlmgK.txt")
async def serve_root_verification_file():
    # Specify the TikTok verification file path
    file_path = "static/tiktokBqCp0CjXfV1QtT9rl09qvRrnXgzDlmgK.txt"
    if os.path.exists(file_path):
        return FileResponse(file_path)  # Serve the file if it exists
    return {"error": "File not found"}

@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request, token: str = Cookie(None)):
    # Log the cookie value to check if the token is being sent
    print(f"Cookie Token: {token}")  # This will appear in your server logs

    if token:
        try:
            # Verify the token (you can implement your token verification function here)
            verify_access_token(token)  # This function verifies the token
            # If the token is valid, redirect to the dashboard with token in URL
            print(f"Redirecting to dashboard with token: {token}")  # Debug log
            return RedirectResponse(url=f"/dashboard?token={token}", status_code=302)
        except HTTPException:
            # If the token is invalid or expired, redirect to login page
            print("Token is invalid or expired.")
            return RedirectResponse(url="/register?form=signin", status_code=302)
    else:
        # If there's no token, render the landing page
        print("No token found in cookie.")  # Debug log
        return templates.TemplateResponse("landingpage.html", {"request": request})



@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, form: str = "signup"):
    return templates.TemplateResponse("registerr.html", {"request": request, "form_type": form})

@app.get("/forgot-password", response_class=HTMLResponse)
async def terms_page(request: Request):
    return templates.TemplateResponse("forgot-password.html", {"request": request})


@app.get("/reset-password")
async def get_reset_password_page(request: Request, token: str):
    try:
        email = get_email_from_token(token)  # Extract the email from the token
    except HTTPException as e:
        logging.error(f"Invalid or expired token: {e}")
        return templates.TemplateResponse(
            "landingpage.html", {"request": request, "error_message": "Invalid or expired reset token."}
        )

    return templates.TemplateResponse("reset-password.html", {"request": request, "token": token})


@app.get("/authenticate", response_class=HTMLResponse)
async def authenticate(request: Request, email: str, token: str):
    return templates.TemplateResponse("authenticate.html", {"request": request, "email": email, "token": token})



@app.get("/dashboard")
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
        
        # Retrieve the user profile from the database using the email
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Generate a random profile photo or fetch one from user data
        # Handle profile photo URL
        if user.profile_photo_url:
            if user.profile_photo_url.startswith("http"):
                profile_photo_url = user.profile_photo_url  # Full URL
            else:
                profile_photo_url = f"{user.profile_photo_url}"  # Local path
        else:
            # Use a default profile photo or generate one
            profile_photo_url = generate_random_profile_photo(user, db)  
        username = user.full_name # Assuming `name` is the column in your `User` table

        # Pass the data to the template for rendering
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "username": username,
            "email": email,
            "profile_photo_url": profile_photo_url
        })

    except HTTPException:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    
@app.get("/dashboard/{section}", response_class=HTMLResponse)
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
    
    
@app.post("/upload-profile-photo")
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

from datetime import datetime

@app.post("/api/content-data/")
async def create_content_data(
    title: str = Form(...),
    description: str = Form(...),
    tags: str = Form(...),
    end_time: str = Form(...),
    image: UploadFile = File(...),
):
    try:
        # Convert the string start and end times into datetime objects
        end_datetime = datetime.fromisoformat(end_time).replace(tzinfo=None)  # Make naive


        # Save the image file to a directory
        file_location = f"uploads/{image.filename}"
        with open(file_location, "wb") as f:
            f.write(await image.read())

        # Save event data (title, start, end, etc.) to the database or a file
        event = {
            "title": title,
            "end": end_datetime.isoformat(),
            "description": description,
            "tags": tags,
            "file_location": file_location,
        }

        # Simulate saving to a database by appending to a file
        events_file_path = "events.json"

        # If the file doesn't exist, initialize an empty list
        if not os.path.exists(events_file_path):
            events = []
        else:
            with open(events_file_path, "r") as event_file:
                events = json.load(event_file)

        events.append(event)

        with open(events_file_path, "w") as event_file:
            json.dump(events, event_file)

        return {"status": "success", "message": "Content data and event saved successfully"}

    except Exception as e:
        print(f"Error: {str(e)}")  # Log the full error
        raise HTTPException(status_code=500, detail=f"Error saving content data: {str(e)}")


@app.get("/calender", response_class=HTMLResponse)
async def calender_page(request: Request):
    return templates.TemplateResponse("calender.html", {"request": request})

@app.get("/api/events")
async def get_events():
    try:
        # Load events from the database or file
        events_file_path = "events.json"
        
        if not os.path.exists(events_file_path):
            raise HTTPException(status_code=404, detail="No events found")

        with open(events_file_path, "r") as event_file:
            events = json.load(event_file)

        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not load events: {str(e)}")


@app.get("/privacy-policy", response_class=HTMLResponse)
async def privacy_policy_page(request: Request):
    return templates.TemplateResponse("privacy-policy.html", {"request": request})

@app.get("/terms-and-conditions", response_class=HTMLResponse)
async def terms_page(request: Request):
    return templates.TemplateResponse("terms-and-conditions.html", {"request": request})





@app.get("/privacy-policy/tiktokCvwcy7TmgBroNQ5qZERcmWUXGj0jXbWl.txt")
async def serve_tiktok_verification_file():
    file_path = "static/tiktokCvwcy7TmgBroNQ5qZERcmWUXGj0jXbWl.txt"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "File not found"}

# Serve TikTok verification file at the terms-and-conditions path
@app.get("/terms-and-conditions/tiktokxArJ8T0W2vPBu9uZTkrMHh0Ikd7Tgsyy.txt")
async def serve_tiktok_verification_file_terms():
    file_path = "static/tiktokxArJ8T0W2vPBu9uZTkrMHh0Ikd7Tgsyy.txt"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "File not found"}


# Route to serve TikTok verification file
@app.get("/auth/tiktok/callback/{filename}")
async def serve_verification_file(filename: str):
    file_path = f"static/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "File not found"}







# TikTok Login URL
@app.get("/login/tiktok")
def tiktok_login():
    auth_url = (
        f"https://www.tiktok.com/auth/authorize/"
        f"?client_key={CLIENT_KEY}&response_type=code"
        f"&redirect_uri={encoded_redirect_uri}&scope=user.info.basic"
    )
    print(f"TikTok Auth URL: {auth_url}")  # Log the generated URL
    return RedirectResponse(auth_url)

# TikTok OAuth2 Callback with better debugging
@app.get("/auth/tiktok/callback")
async def tiktok_callback(request: Request):
    code = request.query_params.get("code")
    error = request.query_params.get("error")

    # Debugging: Log the full request URL
    print(f"Full request URL: {request.url}")
    print(f"Received code: {code}")
    print(f"Received error: {error}")

    if error:
        return templates.TemplateResponse(
            "error.html", {"request": request, "error": f"Authorization failed: {error}"}
        )

    if code:
        token_url = "https://open.tiktokapis.com/v1/oauth/token/"
        payload = {
            "client_key": CLIENT_KEY,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI,
        }
        response = requests.post(token_url, json=payload)
        try:
            response.raise_for_status()
            token_data = response.json()
            print(f"Token response: {token_data}")
            return templates.TemplateResponse("success.html", {"request": request, "data": token_data})
        except requests.exceptions.RequestException as e:
            error_data = e.response.json() if e.response else {}
            print(f"Token fetch error: {error_data}")
            return templates.TemplateResponse(
                "error.html", {"request": request, "error": f"Failed to fetch token: {error_data}"}
            )

    return templates.TemplateResponse(
        "error.html", {"request": request, "error": "No authorization code provided"}
    )
    
    
    
    
@app.get("/sitemap.xml")
async def get_sitemap():
    file_path = "static/sitemap.xml"  # Path to your sitemap in the static folder
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "Sitemap not found"}


@app.get("/robots.txt")
async def get_robots_txt():
    file_path = "static/robots.txt"  # Ensure the path matches your project structure
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "robots.txt not found"}
