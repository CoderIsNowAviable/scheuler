# app/utils/cookies.py

from fastapi import Response, Cookie
from datetime import timedelta

def set_access_token_cookie(response: Response, access_token: str):
    """
    Sets the access token in the response cookies.
    """
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=24 * 60 * 60,  # 24 hours
        secure=False,  # Set to True in production when using HTTPS
        samesite="Lax",  # Adjust based on cross-site requirements
        path="/"  # Cookie will be accessible across the application
    )

def get_access_token_from_cookie(token: str = Cookie(None)):
    """
    Retrieves the access token from the request cookie.
    """
    if token:
        return token
    else:
        raise ValueError("Access token cookie is missing")

def delete_access_token_cookie(response: Response):
    """
    Deletes the access token cookie from the response.
    """
    response.delete_cookie(key="access_token", path="/")
