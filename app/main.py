from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import os
import requests

# Load environment variables
load_dotenv()

CLIENT_KEY = os.getenv("CLIENT_KEY")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

# Initialize FastAPI app
app = FastAPI()

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Directory for uploads
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())
    return {"message": "File uploaded successfully", "file_path": f"/uploads/{file.filename}"}

# Route to serve TikTok verification file
@app.get("/tiktokAQqwgsPnzXVQ9uew3SojqKOd6KcKjFFF", response_class=HTMLResponse)
async def serve_tiktok_verification():
    return "tiktok-developers-site-verification=AQqwgsPnzXVQ9uew3SojqKOd6KcKjFFF"

# TikTok Login URL
@app.get("/login/tiktok")
def tiktok_login():
    auth_url = (
        f"https://www.tiktok.com/auth/authorize/"
        f"?client_key={CLIENT_KEY}&response_type=code"
        f"&redirect_uri={REDIRECT_URI}&scope=user.info.basic"
    )
    return RedirectResponse(auth_url)

# TikTok OAuth2 Callback
@app.get("/auth/tiktok/callback")
async def tiktok_callback(request: Request):
    code = request.query_params.get("code")
    error = request.query_params.get("error")

    if error:
        return {"error": f"Authorization failed: {error}"}

    if code:
        token_url = "https://open.tiktokapis.com/v2/oauth/token/"
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
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to fetch token: {e.response.json()}"}

    return {"error": "No authorization code provided"}

# Landing Page
@app.get("/", response_class=HTMLResponse)
async def read_landing_page(request: Request):
    return templates.TemplateResponse("landingpage.html", {"request": request})
