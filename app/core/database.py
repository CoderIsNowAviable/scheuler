from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create an engine connected to MySQL
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

# Create an engine with connection pooling and pre-ping enabled
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False,  # Disable SQL echoing in logs
    pool_recycle=1800,  # Refresh connections every 30 minutes
    pool_pre_ping=True  # Check if the connection is alive before using it
)
# Create a session factory bound to the engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()