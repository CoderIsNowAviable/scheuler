import logging
import secrets
from fastapi import Cookie,FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
from app.core.database import engine, Base, SessionLocal
from app.routers.user import router as user_router
from app.routers.auth import router as auth_router
from app.routers.pages import router as pages_router
from app.routers.dashboard import router as dashboard_router
from fastapi.middleware.cors import CORSMiddleware
import os
import requests
from dotenv import load_dotenv
from app.utils.jwt import get_email_from_token, verify_access_token
from oauthlib.oauth2 import WebApplicationClient
import urllib.parse
from starlette.middleware.sessions import SessionMiddleware

# Initialize database models
Base.metadata.create_all(bind=engine)

# Load environment variables
load_dotenv()


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

YOUR_SECRET_KEY = os.getenv("YOUR_SECRET_KEY")
app.add_middleware(SessionMiddleware, secret_key=YOUR_SECRET_KEY, session_cookie="session")


TIKTOK_CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY")
TIKTOK_CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET")
TIKTOK_REDIRECT_URI = os.getenv("TIKTOK_REDIRECT_URI")
GOOGLE_CLIENT_ID= os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET=os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI=os.getenv("GOOGLE_REDIRECT_URI")
SCOPES = ["openid", "email", "profile"]
TIKTOK_SCOPE = "user.info.basic"  # Adjust the scope based on what you need
client = WebApplicationClient(GOOGLE_CLIENT_ID)


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






@app.get("/login/tiktok/")
async def auth_tiktok(request: Request):
    csrf_state = secrets.token_urlsafe(16)  # ✅ Generate a secure random state
    request.session["csrfState"] = csrf_state  # ✅ Store CSRF state in session

    print(f"✅ Session Set: csrfState = {csrf_state}")
    scopes = "user.info.basic"
    auth_url = (
        f"https://open.tiktokapis.com/v2/oauth/authorize/?client_key={TIKTOK_CLIENT_KEY}"
        f"&response_type=code&scope={scopes}&redirect_uri={TIKTOK_REDIRECT_URI}&state={csrf_state}"
    )

    return RedirectResponse(url=auth_url)

@app.get("/auth/tiktok/callback/")
async def tiktok_callback(request: Request):
    """Handles TikTok's OAuth callback, exchanges code for an access token, and fetches user info."""

    # Step 1: Extract query parameters
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    error = request.query_params.get("error")
    error_description = request.query_params.get("error_description")
    csrf_state = request.session.get("csrfState")  # Retrieve CSRF state stored in session

    if error:
        # If there's an error parameter, handle the error gracefully
        return {"error": error, "error_description": error_description}
    
    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing 'code' or 'state' parameters")

    if state != csrf_state:
        raise HTTPException(status_code=400, detail="State parameter mismatch")
    decoded_code = urllib.parse.unquote(code)
    # Exchange code for access token
    token_url = "https://open.tiktokapis.com/v2/oauth/token/"
    token_data = {
        "client_key": TIKTOK_CLIENT_KEY,
        "client_secret": TIKTOK_CLIENT_SECRET,
        "code": decoded_code,
        "grant_type": "authorization_code",
        "redirect_uri": TIKTOK_REDIRECT_URI,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=token_data, headers=headers)

    if response.status_code != 200:
        error_message = response.json().get("message", "Unknown error")
        raise HTTPException(status_code=400, detail=f"Failed to get access token: {error_message}")

    # ✅ Extract access token correctly
    response_data = response.json()
    access_token = response_data.get("access_token")
    open_id = response_data.get("open_id")  # TikTok's unique user ID

    if not access_token:
        raise HTTPException(status_code=400, detail="Access token not found")

    # ✅ Fetch user profile info
    user_info_url = "https://open.tiktokapis.com/v2/user/info/"
    user_info_params = {
        "fields": "open_id,union_id,display_name,avatar_url"
    }
    user_info_headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        user_info_response = await client.get(user_info_url, params=user_info_params, headers=user_info_headers)

    if user_info_response.status_code != 200:
        error_message = user_info_response.json().get("message", "Unknown error")
        raise HTTPException(status_code=400, detail=f"Failed to fetch user info: {error_message}")

    user_info = user_info_response.json().get("data", {})

    # ✅ Clear session after successful authentication
    request.session.pop("csrfState", None)

    return {
        "message": "OAuth successful",
        "access_token": access_token,
        "user": {
            "open_id": user_info.get("open_id"),
            "display_name": user_info.get("display_name"),
            "avatar_url": user_info.get("avatar_url"),
        }
    }



    
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

@app.get("/auth/google")
async def google_login(response: Response):
    """Generate Google OAuth URL and redirect user to Google for authentication."""
    
    # Generate the Google OAuth2 URL
    authorization_url = client.prepare_request_uri(
        "https://accounts.google.com/o/oauth2/auth",
        redirect_uri=GOOGLE_REDIRECT_URI,
        scope=" ".join(SCOPES),
        access_type="offline",
        prompt="consent"
    )

    # Store the state parameter in the cookies
    state = os.urandom(24).hex()  # Generate a random state string
    response.set_cookie("oauth_state", state)

    return RedirectResponse(authorization_url)


@app.get("/auth/callback")
async def oauth2_callback(request: Request, oauth_state: str = Cookie(None)):
    """Handle the OAuth2 callback and fetch the user's profile."""
    
    # Extract the code and state from the callback URL
    code = request.query_params.get("code")
    state = request.query_params.get("state")

    # Validate the state parameter to prevent CSRF attacks
    if state != oauth_state:
        return {"error": "State parameter mismatch"}

    if code:
        # Exchange the authorization code for an access token
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code"
        }
        token_response = requests.post(token_url, data=token_data)
        
        if token_response.status_code != 200:
            return {"error": "Failed to get tokens"}

        # Extract the access token
        token_info = token_response.json()
        access_token = token_info.get("access_token")

        # Fetch the user's profile using the access token
        profile_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        profile_response = requests.get(profile_url, headers={"Authorization": f"Bearer {access_token}"})
        
        if profile_response.status_code == 200:
            profile_data = profile_response.json()
            return {"profile": profile_data}
        else:
            return {"error": "Failed to fetch profile"}
    
    return {"error": "No code found in request"}
