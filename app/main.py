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
        "http://127.0.0.1:8000",  # Local development
        "http://localhost:8000",  # Local development
        "https://scheduler-9v36.onrender.com",  # Production domain
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
@app.get("/", response_class=HTMLResponse)
async def read_landing_page(request: Request):
    return templates.TemplateResponse("landingpage.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, form: str = "signup"):
    return templates.TemplateResponse("registerr.html", {"request": request, "form_type": form})

@app.get("/authenticate", response_class=HTMLResponse)
async def authenticate(request: Request, email: str, token: str):
    return templates.TemplateResponse("authenticate.html", {"request": request, "email": email, "token": token})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

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

# TikTok OAuth2 Callback
@app.get("/auth/tiktok/callback")
async def tiktok_callback(request: Request):
    code = request.query_params.get("code")
    error = request.query_params.get("error")
    
    # Debugging: Print received parameters
    print(f"Received code: {code}")
    print(f"Received error: {error}")

    if error:
        return {"error": f"Authorization failed: {error}"}

    if code:
        token_url = "https://open.tiktokapis.com/v1/oauth/token/"
        payload = {
            "client_key": CLIENT_KEY,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI,  # Use the original redirect URI
        }
        response = requests.post(token_url, json=payload)
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to fetch token: {e.response.json()}"}

    return {"error": "No authorization code provided"}
