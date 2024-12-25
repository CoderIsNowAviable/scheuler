from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.core.database import engine, Base, SessionLocal
from app.routers.user import router as user_router
from app.routers.auth import router as auth_router
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


# Initialize database models
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI()





# Dependency to manage the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])

# Routes for frontend
@app.get("/", response_class=HTMLResponse)
async def read_landing_page(request: Request):
    """
    Display the landing page.
    """
    return templates.TemplateResponse("landingpage.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, form: str = "signup"):
    """
    Display the registration page based on the form type.
    """
    return templates.TemplateResponse("registerr.html", {"request": request, "form_type": form})

@app.get("/authenticate", response_class=HTMLResponse)
async def authenticate(request: Request, email: str, token: str):
    """
    Display the authentication page.
    """
    return templates.TemplateResponse("authenticate.html", {"request": request, "email": email, "token": token})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """
    Display the user dashboard.
    """
    return templates.TemplateResponse("dashboard.html", {"request": request})



