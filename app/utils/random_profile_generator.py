import random
from app.models import User  # Ensure to import your User model
from sqlalchemy.orm import Session
from fastapi import HTTPException

def generate_random_profile_photo(user: User, db: Session):
    """
    Generates a random profile photo using an avatar API if it doesn't exist 
    and saves the generated photo URL to the database.
    """
    # Check if the user already has a profile photo
    if user.profile_photo_url:
        return user.profile_photo_url

    try:
        # Generate a unique avatar URL using Multiavatar
        avatar_id = random.randint(1, 1000)  # Random ID for unique avatars
        avatar_url = f"https://api.multiavatar.com/{avatar_id}.png"

        # Save the avatar URL to the user in the database
        user.profile_photo_url = avatar_url
        db.commit()  # Commit the changes to the database

        return avatar_url  # Return the avatar URL

    except Exception as e:
        db.rollback()  # Roll back the transaction in case of error
        print(f"Error generating profile photo: {e}")
        raise HTTPException(status_code=500, detail="Error generating profile photo")
