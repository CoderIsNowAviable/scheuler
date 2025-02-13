import logging
from fastapi.security import OAuth2PasswordBearer

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
import redis
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours
REDIS_HOST = os.getenv("REDIS_HOSTNAME")
REDIS_PORT = int(os.getenv("REDIS_PORT"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")  # Add this if your Redis requires authentication



# OAuth2PasswordBearer setup (for token extraction)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Set up Redis connection
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    decode_responses=True
)


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
    Get the current authenticated user from the session.
    """
    session_user_id = request.session.get("user_id")  # Retrieve user_id from session

    if not session_user_id:
        logger.warning("No user_id found in session")
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Fetch the user from the database
    user = db.query(User).filter(User.id == session_user_id).first()

    if not user:
        logger.warning(f"User with ID {session_user_id} not found in database")
        raise HTTPException(status_code=404, detail="User not found")

    return user

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


# Generate Month Token and Store in Redis
def generate_month_token(user_id):
    expire = datetime.utcnow() + timedelta(days=30)
    payload = {"user_id": user_id, "exp": expire}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    # Store token and expiry in Redis
    redis_client.set(f"month_token:{user_id}", token)
    redis_client.set(f"month_token_expiry:{user_id}", expire.timestamp())

    return token

# Check if Month Token is Expired
def is_month_token_valid(user_id):
    return redis_client.ttl(f"month_token:{user_id}") > 0


# Generate Daily Token
def generate_daily_token(user_id):
    if not is_month_token_valid(user_id):
        raise HTTPException(status_code=401, detail="Month token expired. Please re-authenticate.")

    expire = datetime.utcnow() + timedelta(days=1)
    payload = {"user_id": user_id, "exp": expire}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    redis_client.set(f"daily_token:{user_id}", token)
    redis_client.set(f"daily_token_expiry:{user_id}", expire.timestamp())

    return token

# Check and Update Daily Token
def get_valid_daily_token(user_id):
    expiry_timestamp = redis_client.get(f"daily_token_expiry:{user_id}")

    if not expiry_timestamp or datetime.utcnow().timestamp() > float(expiry_timestamp):
        new_token = generate_daily_token(user_id)
        redis_client.set(f"daily_token:{user_id}", new_token)  # Store new token
        return new_token

    return redis_client.get(f"daily_token:{user_id}")




def validate_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=403, detail="Invalid token")

        # Check token expiration (you can adjust this check based on your needs)
        expiration_time = datetime.utcfromtimestamp(payload["exp"])
        if expiration_time < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Token has expired")

        return user_id  # Return the user ID for use in routes

    except JWTError:
        raise HTTPException(status_code=403, detail="Could not validate credentials")
