from sqlalchemy import NullPool, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("SUPABASE_DB_URL")

if not DATABASE_URL:
    raise ValueError("❌ SUPABASE_DB_URL not found in .env file")

# สำหรับ Supabase - ต้องมี SSL และ timeout
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=40,          # smaller pool since Supabase handles it
    max_overflow=60,
    pool_timeout=30,
    pool_recycle=1800,
    echo=False,
    connect_args={
        "sslmode": "require"
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()