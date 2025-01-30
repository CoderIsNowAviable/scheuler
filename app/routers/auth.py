from fastapi import APIRouter, Depends, HTTPException, Request, Response, Cookie
from sqlalchemy.orm import Session
from datetime import timedelta
import requests, os
from app.core.database import get_db
from app.models import User
from app.utils.jwt import create_access_token
from starlette.responses import RedirectResponse
from dotenv import load_dotenv


load_dotenv()

router = APIRouter()

GOOGLE_CLIENT_ID = "GOOGLE_CLIENT_ID"
GOOGLE_CLIENT_SECRET = "GOOGLE_CLIENT_SECRET"
GOOGLE_REDIRECT_URI = "GOOGLE_REDIRECT_URI"
SCOPES = ["openid", "email", "profile"]



@router.get("/auth/google")
async def google_login(response: Response):
    state = os.urandom(24).hex()
    response.set_cookie("oauth_state", state)
    auth_url = (f"https://accounts.google.com/o/oauth2/auth?client_id={GOOGLE_CLIENT_ID}&"
                f"redirect_uri={GOOGLE_REDIRECT_URI}&response_type=code&scope={' '.join(SCOPES)}&"
                f"access_type=offline&prompt=consent&state={state}")
    return RedirectResponse(auth_url)

@router.get("/auth/callback")
async def google_callback(request: Request, db: Session = Depends(get_db), oauth_state: str = Cookie(None)):
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    if state != oauth_state:
        raise HTTPException(status_code=400, detail="Invalid OAuth state")
    
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
        raise HTTPException(status_code=400, detail="Failed to get Google tokens")
    
    access_token = token_response.json().get("access_token")
    profile_response = requests.get("https://www.googleapis.com/oauth2/v1/userinfo", 
                                    headers={"Authorization": f"Bearer {access_token}"})
    if profile_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch Google profile")
    
    profile_data = profile_response.json()
    email = profile_data.get("email")
    full_name = profile_data.get("name")
    profile_photo = profile_data.get("picture")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(full_name=full_name, email=email, profile_photo_url=profile_photo, is_verified=True, hashed_password="google-oauth")
        db.add(user)
        db.commit()
        db.refresh(user)
    
    access_token = create_access_token(data={"sub": email}, expires_delta=timedelta(hours=24))
    return RedirectResponse(url=f"/dashboard?token={access_token}", status_code=302)
