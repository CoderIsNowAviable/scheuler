from datetime import datetime
import json
import logging
import shutil
from fastapi import Cookie, Depends, FastAPI, Form, HTTPException, Request, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.core.database import engine, Base, SessionLocal
from app.routers.user import router as user_router
from app.routers.auth import router as auth_router
from app.routers.pages import router as pages_router
from app.routers.dashboard import router as dashboard_router
from fastapi.middleware.cors import CORSMiddleware
from urllib.parse import quote
import os
import requests
from dotenv import load_dotenv
from app.utils.jwt import get_email_from_token, verify_access_token
from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from google_auth_oauthlib.flow import Flow
import os
from dotenv import load_dotenv
import requests
from fastapi.templating import Jinja2Templates
from urllib.parse import quote

# Initialize database models
Base.metadata.create_all(bind=engine)

# Load environment variables
load_dotenv()

TIKTOK_CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY")
TIKTOK_CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET")
TIKTOK_REDIRECT_URI = os.getenv("TIKTOK_REDIRECT_URI")

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
encoded_redirect_uri = quote(TIKTOK_REDIRECT_URI, safe="")

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
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
templates = Jinja2Templates(directory="templates")
PROFILE_PHOTO_DIR = "static/profile_photos"
# Include routers
app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(pages_router, prefix="/pages", tags=["pages"])
app.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
os.makedirs("uploads", exist_ok=True)

@app.on_event("startup")
async def startup_event():
    print(f"CLIENT_KEY: {TIKTOK_CLIENT_KEY}")
    print(f"REDIRECT_URI: {TIKTOK_REDIRECT_URI}")
    

    
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
        f"?client_key={TIKTOK_CLIENT_KEY}&response_type=code"
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
            "client_key": TIKTOK_CLIENT_KEY,
            "client_secret": TIKTOK_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": TIKTOK_REDIRECT_URI,
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





CLIENT_SECRETS_FILE = "static/credentials.json"  # Make sure to point to your client secrets file
SCOPES = ["openid", "profile", "email"]  # Define the scopes you need
REDIRECT_URI = "https://scheduler-9v36.onrender.com/auth/callback"


@app.get("/auth/google")
async def google_login():
    """Generate Google OAuth URL and redirect user to Google for authentication."""
    # Create the OAuth 2.0 flow instance
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

    # Generate the Google OAuth2 URL
    authorization_url, state = flow.authorization_url(prompt='consent')  # Ensure prompt=consent for reauthentication
    print(f"Google Auth URL: {authorization_url}")  # Debug log
    return RedirectResponse(authorization_url)

@app.get("/auth/callback")
async def oauth2_callback(request: Request):
    # Log the full callback URL
    authorization_response = str(request.url)
    print(f"Received callback URL: {authorization_response}")

    # Extract the 'code' and 'state' from the URL
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    print(f"Authorization code: {code}, State: {state}")  # Debug the code and state

    # Initialize the flow with client secrets and redirect URI
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

    # Validate the 'state' parameter for security
    if state != request.cookies.get("oauth_state"):
        print("State parameter mismatch, potential security issue.")
        return templates.TemplateResponse(
            "error.html", {"request": request, "error": "State parameter mismatch"}
        )

    if code:
        try:
            # Exchange the authorization code for tokens
            print("Exchanging authorization code for tokens...")
            flow.fetch_token(authorization_response=authorization_response)
            credentials = flow.credentials
            print(f"Access Token: {credentials.token}")  # Debug the token

            # Fetch the user's profile using the credentials
            profile_response = requests.get(
                "https://www.googleapis.com/oauth2/v1/userinfo",
                headers={"Authorization": f"Bearer {credentials.token}"}
            )
            print(f"Profile API response: {profile_response.status_code} - {profile_response.text}")  # Debug profile response

            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                print(f"User profile data: {profile_data}")  # Debug user profile
                return templates.TemplateResponse("user_profile.html", {"request": request, "profile": profile_data})
            else:
                print(f"Failed to fetch profile data: {profile_response.status_code} - {profile_response.text}")
                return templates.TemplateResponse("error.html", {"request": request, "error": "Failed to fetch profile data."})

        except Exception as e:
            print(f"Error during OAuth callback: {e}")
            return templates.TemplateResponse(
                "error.html", {"request": request, "error": f"Error during OAuth callback: {str(e)}"}
            )
    else:
        print("No authorization code received")
        return templates.TemplateResponse(
            "error.html", {"request": request, "error": "No authorization code received"}
        )
