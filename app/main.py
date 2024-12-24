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



# Custom Middleware for Security Headers
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Process the response
        response: Response = await call_next(request)
        
        # Add Security Headers
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self';"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "geolocation=(self); microphone=(); camera=()"
        
        return response


# Add the Security Headers Middleware
app.add_middleware(SecurityHeadersMiddleware)

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



