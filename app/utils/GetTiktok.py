from fastapi import HTTPException, Request, Depends
from sqlalchemy.orm import Session
from app.models.user import User, TikTokAccount  # Import your models
from app.core.database import get_db  # Your database dependency

async def get_tiktok_info(request: Request, db: Session = Depends(get_db)):
    # Check if TikTok session exists in request
    tiktok_session = request.session.get("tiktok_session")

    if not tiktok_session:
        # Retrieve the user_id from the session if TikTok session is missing
        user_id = request.session.get("user_id")

        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")

        # Retrieve TikTok account information from the database
        tiktok_account = db.query(TikTokAccount).filter(TikTokAccount.user_id == user_id).first()

        if not tiktok_account:
            raise HTTPException(status_code=404, detail="TikTok account not linked to the user")

        # Retrieve user information (e.g., user_id)
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Return the TikTok account info and user_id
        return {
            "user_id": user.id,  # Returning user_id from the User table
            "username": tiktok_account.username,
            "profile_picture": tiktok_account.profile_picture,
            "open_id": tiktok_account.openid
        }

    # If TikTok session exists, use it directly
    return {
        "user_id": tiktok_session.get("user_id"),  # Returning user_id from the session
        "username": tiktok_session.get("username"),
        "profile_picture": tiktok_session.get("profile_picture"),
        "open_id": tiktok_session.get("open_id")
    }
