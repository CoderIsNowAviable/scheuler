from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from .user import PendingUser
# app/models/__init__.py
from .user import User  # Importing the User model from users.py
