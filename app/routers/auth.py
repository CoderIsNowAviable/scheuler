from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import PendingUser, User
from app.utils.jwt import create_access_token
from app.utils.email_utils import send_verification_email, generate_verification_code
from app.crud.user import get_verification_code_by_email, clear_verification_code, update_verification_code

router = APIRouter()

@router.post("/send-verification-code")
async def send_verification_code(email: str, db: Session = Depends(get_db)):
    # Generate a 6-character alphanumeric verification code
    verification_code = generate_verification_code()

    # Store the verification code in the database
    update_verification_code(db, email, verification_code)
    
    # Send the verification code to the user's email
    send_verification_email(email, verification_code)
    
    return {"msg": "Verification code sent to your email. Please check your inbox."}

@router.post("/verify-code")
async def verify_code(email: str, verification_code: str, db: Session = Depends(get_db)):
    stored_code = get_verification_code_by_email(db, email)
    if not stored_code:
        raise HTTPException(status_code=400, detail="Verification code not found.")

    if stored_code == verification_code:
        # Clear the verification code after successful verification
        clear_verification_code(db, email)
        
        # Generate JWT or access token (you could also use refresh tokens if needed)
        token = create_access_token(data={"sub": email})
        return {"access_token": token, "token_type": "bearer"}
    
    raise HTTPException(status_code=400, detail="Invalid verification code.")


