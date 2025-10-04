from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
import sys

from .database2 import Base, engine
from .models import Role
from .routers import user_router

 
app = FastAPI(title="Eiei Marketplace User Management")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5000",
        "http://localhost:8000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user_router.router, prefix="/users", tags=["Users"])


# =============== Database Initialization ===============
def init_database():
    """Initialize database tables and default data"""
    print("🔄 Initializing database...")
    
    try:
        # Test connection first
        print("🧪 Testing database connection...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
            print("✅ Database connection successful!")
        
        # Create tables
        print("📋 Creating tables...")
        Base.metadata.create_all(bind=engine)
        
        # Initialize default roles
        db = Session(bind=engine)
        try:
            existing_roles = db.query(Role).all()
            
            if not existing_roles:
                print("➕ Adding default roles (vendor, organizer)...")
                db.add_all([
                    Role(name="vendor"),
                    Role(name="organizer")
                ])
                db.commit()
                print("✅ Default roles created!")
            else:
                print(f"✅ Found {len(existing_roles)} existing roles")
                for role in existing_roles:
                    print(f"   - {role.name}")
        finally:
            db.close()
            
        print("🎉 Database initialization complete!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Database initialization failed!")
        print(f"Error: {str(e)}\n")
        return False


if __name__ == "__main__":
    import uvicorn
    
    # Initialize database before starting server
    if not init_database():
        print("\n⚠️  Do you want to start the server anyway? (y/n): ", end="")
        response = input().strip().lower()
        if response != 'y':
            print("❌ Server startup cancelled")
            sys.exit(1)
    
    # Start server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=7001,
        reload=True
    )