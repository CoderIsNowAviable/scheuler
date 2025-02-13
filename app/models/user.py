from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(200), nullable=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    is_verified = Column(Boolean, default=False)
    verification_code = Column(String(5))
    profile_photo_url = Column(String(255), default=None)
    month_token = Column(String(255), nullable=True)


    # Relationships
    pending_user = relationship("PendingUser", back_populates="owner", uselist=False)
    tiktok_account = relationship("TikTokAccount", back_populates="user", uselist=False)
    contents = relationship("Content", back_populates="user")

class PendingUser(Base):
    __tablename__ = "pending_users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    full_name = Column(String(200), nullable=True)
    verification_code = Column(String(5))
    verification_code_expiry = Column(DateTime, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="pending_user")

    def is_code_expired(self):
        """Helper method to check if the verification code has expired"""
        return self.verification_code_expiry < datetime.utcnow()

class TikTokAccount(Base):
    __tablename__ = "tiktok_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)  # One user, one TikTok account
    openid = Column(String(255), unique=True, index=True)  # TikTok OpenID
    username = Column(String(255), nullable=False)
    profile_picture = Column(String(500), nullable=True)  # Increase to 500 characters
    access_token = Column(String(500), nullable=True)  # ➜ Store TikTok Access Token

    user = relationship("User", back_populates="tiktok_account")

class Content(Base):
    __tablename__ = "contents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))  # Who created this content
    platform = Column(String(50), nullable=False, default="tiktok")  # e.g., TikTok, Instagram
    media_url = Column(String(255), nullable=False)  # Storage URL of the video/image
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    tags = Column(String(255), nullable=True)  # Comma-separated tags
    scheduled_time = Column(DateTime, nullable=True)  # When to post

    user = relationship("User", back_populates="contents")
