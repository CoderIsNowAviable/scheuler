import logging
from fastapi import HTTPException, Depends
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from typing import Optional
from fastapi.requests import Request
from sqlalchemy.orm import Session
from app.models import User
from app.core.database import get_db

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def create_access_token(data: dict, expires_delta: timedelta = None):
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=1))  # Default to 1 hour if no expiry is provided
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.error("Token expired")
        raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError as e:
        logger.error(f"JWT Error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_user(request: Request, db: Session = Depends(get_db)):
    """
    Get the current authenticated user from the token or session.
    """
    token = request.cookies.get("access_token")  # Or from the Authorization header

    if not token:
        logger.warning("No access token found in request")
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        user_data = verify_access_token(token)  # Decode the token and retrieve user data
        user_id = user_data.get("sub")

        if not user_id:
            logger.warning("User ID not found in token")
            raise HTTPException(status_code=401, detail="Invalid token or user data missing")

        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            logger.warning(f"User with ID {user_id} not found in database")
            raise HTTPException(status_code=404, detail="User not found")

        return user
    except Exception as e:
        logger.error(f"Error in get_current_user: {e}")
        raise HTTPException(status_code=401, detail="Token is invalid or expired")


def get_email_from_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid token")

