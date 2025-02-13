import logging
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, Depends, Response
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from typing import Optional
from fastapi.requests import Request
from sqlalchemy.orm import Session
from app.models import User
from app.core.database import get_db
import redis
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
    Get the current authenticated user from session or JWT token.
    If the monthly token is expired, redirect user to login.
    """

    # 1️⃣ Check session first
    session_user_id = request.session.get("user_id")
    if session_user_id:
        user = db.query(User).filter(User.id == session_user_id).first()
        if user:
            logger.info(f"User {session_user_id} authenticated via session")
            return user
        logger.warning(f"User ID {session_user_id} from session not found in DB")

    # 2️⃣ Check for JWT token in cookies
    month_token = request.cookies.get("month_token")
    if not month_token:
        logger.warning("No session and no JWT token found. Redirecting to login.")
        return RedirectResponse(url="/login")

    try:
        # Decode JWT token
        payload = jwt.decode(month_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        exp_timestamp = payload.get("exp")

        # 3️⃣ If token expired, force login
        if datetime.utcnow().timestamp() > exp_timestamp:
            logger.warning(f"Monthly token expired for user {user_id}. Redirecting to login.")
            return RedirectResponse(url="/login")

        # 4️⃣ Validate user from database
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning(f"User ID {user_id} from token not found in DB. Redirecting to login.")
            return RedirectResponse(url="/login")

        return user  # ✅ User authenticated via JWT

    except JWTError:
        logger.error("Invalid JWT token. Redirecting to login.")
        return RedirectResponse(url="/login")

def get_email_from_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid token")

def get_email_from_Ctoken(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=403, detail="Could not validate credentials")
        return email
    except JWTError:
        raise HTTPException(status_code=403, detail="Could not validate credentials")



def is_month_token_valid(request: Request, user_id: int, db: Session):
    """
    Check if the month token is valid:
    - Token should match the one stored in the database for the user.
    - Token should not be expired.
    """
    # 1️⃣ Get the month token stored in the database for the user
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db_month_token = user.month_token

    # 2️⃣ Get the month token from the session
    month_token_from_session = request.session.get("month_token")
    if not month_token_from_session:
        raise HTTPException(status_code=401, detail="Month token missing")

    # 3️⃣ Decode the month token to check for its validity
    try:
        # Decode the JWT and extract the expiry time
        payload = jwt.decode(month_token_from_session, SECRET_KEY, algorithms=[ALGORITHM])
        exp_timestamp = payload.get("exp")

        # 4️⃣ Check if token matches the one in the database and if it's expired
        if db_month_token != month_token_from_session:
            raise HTTPException(status_code=401, detail="Invalid month token")

        # 5️⃣ Check if the token has expired
        if datetime.utcnow().timestamp() > exp_timestamp:
            raise HTTPException(status_code=401, detail="Month token expired")

        return True

    except JWTError as e:
        raise HTTPException(status_code=401, detail="Invalid month token")


def generate_daily_token(user_id):
    """Generate a new daily token if the month token is still valid."""
    expire = datetime.utcnow() + timedelta(days=1)

    payload = {"user_id": user_id, "exp": expire.timestamp()}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return token


def get_valid_daily_token(request: Request, response: Response):
    """
    Check if the daily token in session is valid.
    If expired or missing, generate a new one and store it in the session.
    """
    daily_token = request.session.get("daily_token")

    if daily_token:
        try:
            payload = jwt.decode(daily_token, SECRET_KEY, algorithms=[ALGORITHM])
            exp_timestamp = payload.get("exp")

            if datetime.utcnow().timestamp() <= exp_timestamp:
                return daily_token  # Token is valid, return it

        except JWTError:
            logger.warning("Invalid or expired daily token. Generating a new one.")

    # If expired or missing, generate a new token
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User session missing. Please re-authenticate.")

    new_token = generate_daily_token(user_id)

    # Store the new daily token in session
    request.session["daily_token"] = new_token

    return new_token
