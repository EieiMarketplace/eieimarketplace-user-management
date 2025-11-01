from sqlalchemy import create_engine
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
    pool_pre_ping=True,          # ตรวจสอบ connection ก่อนใช้
    pool_size=1000,                 # จำนวน connection ใน pool
    max_overflow=500,             # connection เพิ่มเติมสูงสุด
    pool_recycle=3600,         # recycle connection ทุก 1 ชั่วโมง
    echo=False,                  # Set True เพื่อดู SQL queries
    connect_args={
        "connect_timeout": 30,   # Timeout 10 วินาที
        "sslmode": "require",    # บังคับใช้ SSL (สำคัญ!)
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
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