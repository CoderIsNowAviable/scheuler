from datetime import timedelta
from urllib import request
from dotenv import load_dotenv
from fastapi import APIRouter, Form, HTTPException, Depends, Request, status, Cookie
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.models.user import PendingUser, User
from app.schemas.user import PasswordResetRequest, ResendCodeRequest, ResetPasswordRequest, VerifyCodeRequest
from app.utils.email_utils import generate_verification_code, send_password_reset_email, send_verification_email
from app.utils.jwt import create_access_token,  get_email_from_token, generate_month_token
from app.utils.password import verify_password, hash_password
from app.core.database import get_db
import logging
import os
from itsdangerous import TimestampSigner, BadSignature

load_dotenv()

router = APIRouter()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
# Secret key for signing cookies
COOKIE_SECRET_KEY = os.getenv("COOKIE_SECRET_KEY")
print(f"DEBUG: COOKIE_SECRET_KEY = {COOKIE_SECRET_KEY}")

if not COOKIE_SECRET_KEY:
    raise ValueError("COOKIE_SECRET_KEY is not set")
signer = TimestampSigner(COOKIE_SECRET_KEY)
@router.post("/signup")
async def signup(
    full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
  # Check if user already exists
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    if db.query(PendingUser).filter(PendingUser.email == email).first():
        raise HTTPException(status_code=400, detail="Pending verification already exists for this email")
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
async def signin(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    logger.debug("Signin attempt for email: %s", email)

    # Step 1: Check if user_id exists in session
    user_id = request.session.get("user_id")
    if user_id:
        logger.info("User %s found in session, fetching user data...", user_id)
        user = db.query(User).filter(User.id == user_id).first()
    else:
        # If no user_id in session, fetch user by email
        user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Step 2: Check if user is pending verification
    pending_user = db.query(PendingUser).filter(PendingUser.email == email).first()
    if pending_user:
        access_token = create_access_token(data={"sub": email}, expires_delta=timedelta(hours=1))
        response = RedirectResponse(url=f"/authenticate?email={email}&token={access_token}", status_code=302)
        response.set_cookie(key="access_token", value=access_token, httponly=True, secure=True, samesite="Strict")
        return response

    # Step 3: Handle Google OAuth Login
    if user.hashed_password == "google-oauth":
        logger.info(f"User {user.id} is logging in via Google OAuth")

    else:
        # Manual login with password verification
        if not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Invalid password")

    # Step 4: Generate & store a new month token
    month_token = generate_month_token(user.id)
    logger.debug(f"Generated month token for user {user.id}: {month_token}")

    user.month_token = month_token
    db.commit()
    db.refresh(user)

    # Step 5: Store session details
    request.session["user_id"] = user.id
    request.session["month_token"] = month_token
    session_token = signer.sign(f"user_session_{user.id}").decode()

    # Step 6: Set cookie and redirect
    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,  # Set to False in development
        samesite="None",
        max_age=60 * 60 * 24 * 30,  # 30 days
        path="/"  # Makes the cookie available on all pages
    )

    return response


@router.post("/verify-code")
async def verify_code(request: VerifyCodeRequest, db: Session = Depends(get_db)):
    logging.info(f"Request received: {request}")
    print(f"Request data: {request}")  # Log request

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
        is_verified=True
    )
    db.add(new_user)
    db.commit()

    db.delete(pending_user)
    db.commit()

    # Generate an access token after successful verification
    access_token = create_access_token(data={"sub": email}, expires_delta=timedelta(hours=24))
    logging.info(f"Verification successful, token generated: {access_token}")

    # Return the access token in the response body
    return {"message": "Verification successful!", "access_token": access_token}



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




@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)
