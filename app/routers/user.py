from datetime import timedelta
from fastapi import APIRouter, Form, HTTPException, Depends, Request, Response, status, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.models.user import PendingUser, User
from app.schemas.user import PasswordResetRequest, ResetPasswordRequest, VerifyCodeRequest
from app.utils.email_utils import generate_verification_code, send_password_reset_email, send_verification_email
from app.utils.jwt import create_access_token, verify_access_token, get_email_from_token
from app.utils.password import verify_password, hash_password
from app.core.database import get_db
import logging

router = APIRouter()

logging.basicConfig(level=logging.DEBUG)

@router.post("/signup")
async def signup(
    full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    existing_user = db.query(User).filter(User.email == email).first()
    pending_user = db.query(PendingUser).filter(PendingUser.email == email).first()
    if existing_user or pending_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    hashed_password = hash_password(password)

    verification_code, expires_at = generate_verification_code()

    if isinstance(verification_code, tuple):
        verification_code = verification_code[0]  # Extract just the code (string)

    new_pending_user = PendingUser(
        full_name=full_name,
        email=email,
        hashed_password=hashed_password,
        verification_code=verification_code,
        verification_code_expiry=expires_at,
    )

    try:
        db.add(new_pending_user)
        db.commit()
        db.refresh(new_pending_user)
        send_verification_email(email, verification_code)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save user: {str(e)}")

    access_token = create_access_token(data={"sub": email}, expires_delta=timedelta(hours=1))

    return RedirectResponse(url=f"/authenticate?email={email}&token={access_token}", status_code=302)

@router.post("/signin")
async def signin(response: Response, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    pending_user = db.query(PendingUser).filter(PendingUser.email == email).first()

    if pending_user:
        access_token = create_access_token(data={"sub": email}, expires_delta=timedelta(hours=1))
        response.set_cookie(key="access_token", value=access_token, httponly=True, secure=True, samesite="Strict")
        return RedirectResponse(url=f"/authenticate?email={email}", status_code=302)

    if user:
        if not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid password")

    access_token = create_access_token(data={"sub": email}, expires_delta=timedelta(hours=1))
    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=False, samesite="Strict", path="../utils/cookies.py")
    
    return RedirectResponse(f"/users/dashboard", status_code=302)



@router.post("/verify-code")
async def verify_code(request: VerifyCodeRequest, db: Session = Depends(get_db)):
    email = request.email
    verification_code = request.verification_code

    pending_user = db.query(PendingUser).filter(PendingUser.email == email).first()
    if not pending_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if pending_user.is_code_expired():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification code has expired")

    if pending_user.verification_code != verification_code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification code")

    new_user = User(
        full_name=pending_user.full_name,
        email=pending_user.email,
        hashed_password=pending_user.hashed_password,
        is_verified=True,
    )
    db.add(new_user)
    db.commit()

    db.delete(pending_user)
    db.commit()

    return {"message": "Verification successful!"}

@router.post("/request-password-reset")
async def request_password_reset(request: PasswordResetRequest, db: Session = Depends(get_db)):
    email = request.email
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    reset_token = create_access_token(data={"sub": email}, expires_delta=timedelta(hours=1))
    reset_link = f"https://scheduler-9v36.onrender.com/reset-password?token={reset_token}"
    send_password_reset_email(email, reset_link)

    return {"message": "Password reset link has been sent to your email"}

@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    token = request.token
    new_password = request.new_password
    try:
        email = get_email_from_token(token)
    except HTTPException as e:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    hashed_password = hash_password(new_password)
    user.hashed_password = hashed_password
    db.commit()

    return {"message": "Password has been reset successfully!"}

@router.get("/dashboard")
async def dashboard(request: Request, token: str = Cookie(None)):
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")

    try:
        user_data = verify_access_token(token)
        return {"message": f"Welcome, {user_data['sub']}"}
    except HTTPException:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


@router.get("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out successfully"}
