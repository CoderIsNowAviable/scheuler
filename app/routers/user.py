from datetime import datetime
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
from app.models.user import PendingUser
from app.utils.email_utils import generate_verification_code, send_verification_email
from app.utils.jwt import create_access_token
from app.utils.password import verify_password, hash_password
from app.schemas.user import SigninRequest, UserCreate, VerifyCodeRequest
from app.core.database import get_db
from app.models import User



router = APIRouter()


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

    # Generate a 5-digit verification code
    verification_code = generate_verification_code()

    # Create a new pending user
    new_pending_user = PendingUser(
        full_name=full_name,
        email=email,
        hashed_password=hashed_password,
        verification_code=verification_code
    )
    db.add(new_pending_user)
    db.commit()
    db.refresh(new_pending_user)

    # Send the verification code via email
    try:
        send_verification_email(email, verification_code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

    # Create an access token
    access_token = create_access_token(data={"sub": email})

    # Redirect to the authentication page
    return RedirectResponse(url=f"/authenticate?email={email}&token={access_token}", status_code=302)



@router.post("/signin")
async def signin(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Strip whitespace from email and password
    email = email.strip()
    password = password.strip()

    # Check if the user exists
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    # Verify the password
    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    # Generate JWT token
    access_token = create_access_token(data={"sub": user.email})

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/verify-code")
async def verify_code(request: VerifyCodeRequest, db: Session = Depends(get_db)):
    email = request.email
    verification_code = request.verification_code

    # Verify the pending user exists
    pending_user = db.query(PendingUser).filter(PendingUser.email == email).first()
    if not pending_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

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