# app/utils/cookies.py

from fastapi import Response, Cookie
from datetime import timedelta
from app.utils.jwt import create_access_token  # Assuming you are using JWT for creating access tokens

def set_access_token_cookie(response: Response, access_token: str):
    """
    Sets the access token in the response cookies.
    """
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=24 * 60 * 60,  # 24 hours
        secure=False,  # Only send cookies over HTTPS
        samesite="Lax"  # Prevents the cookie from being sent with cross-site requests
    )

def get_access_token_from_cookie(token: str = Cookie(None)):
    """
    Retrieves the access token from the request cookie.
    """
    return token

def delete_access_token_cookie(response: Response):
    """
    Deletes the access token cookie from the response.
    """
    response.delete_cookie(key="access_token")
