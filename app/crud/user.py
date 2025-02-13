from datetime import datetime, timedelta  # Add this import
from sqlalchemy.orm import Session
from app import models
from app import schemas
from app.models import user
from app.utils.password import verify_password
from pydantic import BaseModel
from app.schemas import user as user_schema
from app.models import user as user_model
from app.utils.password import hash_password
from app.schemas.user import UserCreate
from app.models.user import PendingUser, User

# Create User
# Get a user by email
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

# Create a new user
def create_user(db: Session, user: schemas.user.UserCreate):
    db_user = models.User(email=user.email, hashed_password=user.password,month_token=user.month_token
)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
# For user registration
class UserCreate(BaseModel):
    email: str
    password: str  # This is plaintext password, which will be hashed
    full_name: str

    class Config:
        from_attributes = True

# For user login
class UserLogin(BaseModel):
    email: str
    password: str

# Authenticate User (Login)
def authenticate_user(db: Session, email: str, password: str):
    user = db.query(user.User).filter(user.User.email == email).first()
    if user and verify_password(password, user.hashed_password):
        return user
    return None

# Read User
def get_user(db: Session, user_id: int):
    return db.query(user.User).filter(user.User.id == user_id).first()

# Update User
def update_user(db: Session, user_id: int, user_data: user_schema.UserUpdate):
    db_user = db.query(user.User).filter(user.User.id == user_id).first()
    if db_user:
        if user_data.email:
            db_user.email = user_data.email
        if user_data.password:
            db_user.hashed_password = user_data.password
        if user_data.full_name:
            db_user.full_name = user_data.full_name
        db.commit()
        db.refresh(db_user)
        return db_user
    return None

# Delete User
def delete_user(db: Session, user_id: int):
    db_user = db.query(user.User).filter(user.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return db_user
    return None

def update_verification_code(db: Session, email: str, verification_code: str):
    """Update the verification code for a given email."""
    pending_user = db.query(PendingUser).filter(PendingUser.email == email).first()
    if pending_user:
        pending_user.verification_code = verification_code
        db.commit()

def get_verification_code_by_email(db: Session, email: str):
    """Retrieve the verification code for a given email."""
    pending_user = db.query(PendingUser).filter(PendingUser.email == email).first()
    if pending_user:
        return pending_user.verification_code
    return None

def clear_verification_code(db: Session, email: str):
    """Clear the verification code for a given email."""
    pending_user = db.query(PendingUser).filter(PendingUser.email == email).first()
    if pending_user:
        pending_user.verification_code = None
        db.commit()
