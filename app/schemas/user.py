# app/schemas/user.py
from pydantic import BaseModel, EmailStr
from typing import Optional


# Shared properties (e.g., response data)
class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None


# Properties required for user creation (e.g., request payload)
class UserCreate(BaseModel):
    full_name: str
    email: str
    password: str

    class Config:
        from_attributes = True
# Properties for response (e.g., what the API returns)
class User(UserBase):
    id: int

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True  # Allows conversion of SQLAlchemy models to Pydantic models

class UserLogin(BaseModel):
    username: str
    password: str
    
    class Config:
        from_attributes = True  # 'orm_mode' has been renamed to 'from_attributes' in Pydantic V2

class UserUpdate(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    full_name: Optional[str] = None

    class Config:
        from_attributes = True  # Again, using 'from_attributes' instead of 'orm_mode' in V2




class SigninRequest(BaseModel):
    email: str
    password: str

        

    
class VerifyCodeRequest(BaseModel):
    email: str
    verification_code: str
    
class ResendCodeRequest(BaseModel):
    user_email: str
    


class PasswordResetRequest(BaseModel):
    email: EmailStr
    
    
class PasswordResetRequest(BaseModel):
    token: str
    new_password: str