import random
from PIL import Image, ImageDraw
import os
from app.models import User  # Make sure to import your User model
from sqlalchemy.orm import Session

PROFILE_PHOTOS_PATH = "static/profile_photos"

# Ensure the profile_photos directory exists
os.makedirs(PROFILE_PHOTOS_PATH, exist_ok=True)

def generate_random_profile_photo(user: User, db: Session):
    """Generates a random profile photo for the user if it doesn't exist and saves it permanently."""
    
    # Check if the user already has a profile photo
    if user.profile_photo_url:
        return user.profile_photo_url
    
    img_size = 200
    file_name = f"profile_{user.id}.png"  # Use user ID to make the filename unique
    file_path = os.path.join(PROFILE_PHOTOS_PATH, file_name)
    
    # Create a blank image
    image = Image.new("RGB", (img_size, img_size), color="white")
    draw = ImageDraw.Draw(image)

    # Randomize background color
    bg_color = tuple(random.randint(0, 255) for _ in range(3))
    draw.rectangle([(0, 0), (img_size, img_size)], fill=bg_color)

    # Add random circles
    for _ in range(random.randint(5, 10)):
        x1, y1 = random.randint(0, img_size // 2), random.randint(0, img_size // 2)
        x2, y2 = random.randint(img_size // 2, img_size), random.randint(img_size // 2, img_size)
        circle_color = tuple(random.randint(0, 255) for _ in range(3))
        draw.ellipse([x1, y1, x2, y2], fill=circle_color, outline="black")

    # Add random initial
    initial = chr(random.randint(65, 90))  # Random letter (A-Z)
    text_color = tuple(random.randint(0, 255) for _ in range(3))
    draw.text((img_size // 3, img_size // 3), initial, fill=text_color)

    # Save the image
    image.save(file_path)

    # Save the profile photo URL to the user in the database
    user.profile_photo_url = f"/{file_path}"  # Save the relative URL
    db.commit()  # Commit the changes to the database

    return f"/{file_path}"  # Return the relative file path
