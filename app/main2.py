from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
import sys

from .database2 import Base, engine
from .models import Role
from .routers import user_router

# สร้าง FastAPI app
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
        print("✅ Tables created successfully!")
        
        # Initialize default roles
        print("👥 Checking default roles...")
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
        print("=" * 70)
        print("Troubleshooting:")
        print("1. Check .env file has correct SUPABASE_DB_URL")
        print("2. Verify your database password is correct")
        print("3. Ensure SSL is enabled (sslmode=require)")
        print("4. Try Transaction Pooler (port 6543) instead of 5432")
        print("5. Check firewall/antivirus settings")
        print("=" * 70)
        return False


# Initialize on startup
@app.on_event("startup")
async def startup_event():
    """Run when application starts"""
    success = init_database()
    if not success:
        print("\n⚠️  WARNING: Database initialization failed!")
        print("   API will start but database operations may fail.\n")


# =============== Health Check Endpoints ===============
@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Eiei Marketplace User Management API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
def health_check():
    """Health check endpoint with database status"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        db = Session(bind=engine)
        try:
            role_count = db.query(Role).count()
            db_status = "connected"
        finally:
            db.close()
            
        return {
            "status": "healthy",
            "database": db_status,
            "roles": role_count
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }


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
        "app.main2:app",
        host="0.0.0.0",
        port=7001,
        reload=True
    )