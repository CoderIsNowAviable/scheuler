from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(200), nullable=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    is_verified = Column(Boolean, default=False)
    verification_code = Column(String(5))
    pending_users = relationship("PendingUser", back_populates="owner")

class PendingUser(Base):
    __tablename__ = "pending_users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    full_name = Column(String(200), nullable=True)
    verification_code = Column(String(5))
    verification_code_expiry = Column(DateTime, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="pending_users")
    
    def is_code_expired(self):
        """Helper method to check if the verification code has expired"""
        return self.verification_code_expiry < datetime.utcnow()