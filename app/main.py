from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.core.database import engine, Base, SessionLocal
from app.routers.user import router as user_router
from app.routers.auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
from urllib.parse import quote
import os
import requests
from dotenv import load_dotenv

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
        "https://scheduler-9v36.onrender.com"
        "https://scheduler-9v36.onrender.com",
        "https://scheduler-9v36.onrender.com/terms-and-conditions"
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

@app.on_event("startup")
async def startup_event():
    print(f"CLIENT_KEY: {CLIENT_KEY}")
    print(f"REDIRECT_URI: {REDIRECT_URI}")

# Routes for frontend
@app.get("/")
async def root(request: Request):
    """
    Serve the root page, and also handle TikTok verification if the correct file is requested.
    """
    verification_filename = "tiktok1mlPqbmkhePwn452hhO3qnADJdhqrsNB.txt"  # Your verification file name
    file_path = os.path.join("static", verification_filename)

    # If the verification file is requested, return it directly
    if request.query_params.get("verify") == "true" and os.path.exists(file_path):
        return FileResponse(file_path)
    
    # Otherwise, render the regular landing page or other content
    return templates.TemplateResponse("landingpage.html", {"request": request})





@app.get("/features", response_class=HTMLResponse)
async def features_page(request: Request):
    return templates.TemplateResponse("features.html", {"request": request})

@app.get("/about", response_class=HTMLResponse)
async def about_page(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/contact", response_class=HTMLResponse)
async def contact_page(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})

@app.get("/help", response_class=HTMLResponse)
async def help_page(request: Request):
    return templates.TemplateResponse("help.html", {"request": request})

@app.get("/privacy-policy", response_class=HTMLResponse)
async def privacy_policy_page(request: Request):
    return templates.TemplateResponse("privacy-policy.html", {"request": request})

@app.get("/terms-and-conditions", response_class=HTMLResponse)
async def terms_page(request: Request):
    return templates.TemplateResponse("terms-and-conditions.html", {"request": request})







@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, form: str = "signup"):
    return templates.TemplateResponse("registerr.html", {"request": request, "form_type": form})

@app.get("/forgot-password", response_class=HTMLResponse)
async def terms_page(request: Request):
    return templates.TemplateResponse("forgot-password.html", {"request": request})




@app.get("/authenticate", response_class=HTMLResponse)
async def authenticate(request: Request, email: str, token: str):
    return templates.TemplateResponse("authenticate.html", {"request": request, "email": email, "token": token})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})




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