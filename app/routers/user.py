from datetime import datetime, timedelta
from fastapi import APIRouter, Form, HTTPException, Depends, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session
from app import models
from app.crud.user import (
    create_user,
    get_user_by_email,
    update_verification_code,
    clear_verification_code,
)
from app.core.database import SessionLocal
from app.models.user import PendingUser
from app.utils.email_utils import generate_verification_code, send_verification_email
from app.utils.jwt import create_access_token
from app.utils.password import verify_password, hash_password
from app.schemas.user import SigninRequest, UserCreate, VerifyCodeRequest, ResendCodeRequest
from app.core.database import get_db
from app.models import User
import logging



router = APIRouter()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

logging.basicConfig(level=logging.DEBUG)
logging.basicConfig()

templates = Jinja2Templates(directory="app/templates")



@router.post("/signup")
async def signup(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Check if the user already exists in the PendingUser or User table
    existing_user = db.query(User).filter(User.email == email).first()
    pending_user = db.query(PendingUser).filter(PendingUser.email == email).first()
    if existing_user or pending_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    # Hash the password
    hashed_password = hash_password(password)

    # Generate a 5-digit verification code and expiration time
    verification_code, expires_at = generate_verification_code()  # This returns a tuple

    # Ensure that verification_code is just the string (not a tuple)
    if isinstance(verification_code, tuple):
        verification_code = verification_code[0]  # Extract just the code (string)

    # Create a new pending user
    new_pending_user = PendingUser(
        full_name=full_name,
        email=email,
        hashed_password=hashed_password,
        verification_code=verification_code,  # Now it's just a string
        verification_code_expiry=expires_at  # Correct datetime object
    )

    try:
        db.add(new_pending_user)
        db.commit()
        db.refresh(new_pending_user)

        # Send the verification code via email
        send_verification_email(email, verification_code)

    except Exception as e:
        db.rollback()  # Rollback in case of any error
        raise HTTPException(status_code=500, detail=f"Failed to save user: {str(e)}")

    # Create an access token
    access_token = create_access_token(data={"sub": email})

    # Redirect to the authentication page
    return RedirectResponse(url=f"/authenticate?email={email}&token={access_token}", status_code=302)



@router.post("/signin")
async def signin(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    # Check if the user exists in the User table
    user = db.query(User).filter(User.email == email).first()
    pending_user = db.query(PendingUser).filter(PendingUser.email == email).first()

    if pending_user:
        # If the user is in the PendingUser table, they need to verify their code
        access_token = create_access_token(data={"sub": email})
        return RedirectResponse(url=f"/authenticate?email={email}&token={access_token}", status_code=302)

    if user:
        # If the user is in the User table and verified, proceed with login
        if not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid password")

        access_token = create_access_token(data={"sub": email})
        return RedirectResponse(url="/dashboard.html", status_code=302)

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")



@router.post("/verify-code")
async def verify_code(request: VerifyCodeRequest, db: Session = Depends(get_db)):
    email = request.email
    verification_code = request.verification_code

    # Verify the pending user exists
    pending_user = db.query(PendingUser).filter(PendingUser.email == email).first()
    if not pending_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Check if the code has expired
    if pending_user.is_code_expired():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification code has expired")

    # Check the verification code
    if pending_user.verification_code != verification_code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification code")

    # Transfer data to the User table
    new_user = User(
        full_name=pending_user.full_name,
        email=pending_user.email,
        hashed_password=pending_user.hashed_password,
        is_verified=True
    )
    db.add(new_user)
    db.commit()

    # Remove the entry from the PendingUser table
    db.delete(pending_user)
    db.commit()

    return {"message": "Verification successful!"}

@router.post("/resend-verification-code")
def resend_verification_code(request: ResendCodeRequest, db: Session = Depends(get_db)):
    logging.info(f"Received request with email: {request.user_email}")
    user_email = request.user_email

    try:
        # Find the pending user by email
        pending_user = db.query(PendingUser).filter(PendingUser.email == user_email).first()

        if pending_user:
            # Check if the verification code has expired
            if pending_user.is_code_expired():
                # Generate a new verification code and expiration time
                verification_code, expires_at = generate_verification_code()

                # Ensure that verification_code is a string and expires_at is a datetime object
                if isinstance(verification_code, tuple):
                    verification_code = verification_code[0]  # Extract the code if it's a tuple

                # Update the pending user's verification code and expiry time
                update_params = {
                    'verification_code': verification_code,
                    'verification_code_expiry': expires_at,
                    'pending_users_id': pending_user.id  # Use the pending user's ID
                }

                # Log the parameters to debug
                logging.info(f"Update parameters: {update_params}")

                # Update the pending user in the database
                db.query(PendingUser).filter(PendingUser.id == update_params['pending_users_id']).update({
                    PendingUser.verification_code: update_params['verification_code'],
                    PendingUser.verification_code_expiry: update_params['verification_code_expiry']
                })
                db.commit()

                logging.info(f"Verification code resent to {user_email}, code: {verification_code}, expires at: {expires_at}")

                # Send the verification email
                send_verification_email(user_email, verification_code)

                return {"message": "Verification code resent successfully"}
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification code is still valid.")
        else:
            raise HTTPException(status_code=404, detail="User not found")

    except Exception as e:
        logging.error(f"Error during operation: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")