import logging
from fastapi import Cookie, Depends, FastAPI, HTTPException, Request, UploadFile, File
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

# Include routers
app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(pages_router, prefix="/pages", tags=["pages"])


@app.on_event("startup")
async def startup_event():
    print(f"CLIENT_KEY: {CLIENT_KEY}")
    print(f"REDIRECT_URI: {REDIRECT_URI}")

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

        # Retrieve the user profile from the database using the email
        user = db.query(User).filter(User.email == email).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Generate a random profile photo or fetch one from user data
        profile_photo_url = generate_random_profile_photo(user, db)  # Replace with actual logic if necessary
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



@app.get("/privacy-policy", response_class=HTMLResponse)
async def privacy_policy_page(request: Request):
    return templates.TemplateResponse("privacy-policy.html", {"request": request})

@app.get("/terms-and-conditions", response_class=HTMLResponse)
async def terms_page(request: Request):
    return templates.TemplateResponse("terms-and-conditions.html", {"request": request})



@app.get("/tiktokBqCp0CjXfV1QtT9rl09qvRrnXgzDlmgK.txt")
async def serve_root_verification_file():
    # Specify the TikTok verification file path
    file_path = "static/tiktokBqCp0CjXfV1QtT9rl09qvRrnXgzDlmgK.txt"
    if os.path.exists(file_path):
        return FileResponse(file_path)  # Serve the file if it exists
    return {"error": "File not found"}

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