import asyncio
import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
import sys
import aio_pika

from .services.service import UserService
from .database2 import Base, engine
from .models import Role
from .routers import user_router
import logging
from . import database2

logger = logging.getLogger(__name__)

_connection = None

from dotenv import load_dotenv
load_dotenv()

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "")
print("RABBIT MQ")

# ---------- RabbitMQ Listener ----------
# RABBITMQ_URL = "amqp://guest:guest@localhost:5672/"
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "")
print("RABBIT MQ")
EXCHANGE_NAME = "user_info"
QUEUE_NAME = "user_info_queue"
ROUTING_KEY = "user_info.status"

def get_db():
    db = database2.SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
async def listen_rabbitmq():
    while True:
        try:
            connection = await aio_pika.connect_robust(RABBITMQ_URL)
            channel = await connection.channel()
            exchange = await channel.declare_exchange(EXCHANGE_NAME, aio_pika.ExchangeType.TOPIC, durable=True)
            queue = await channel.declare_queue("user_info_queue", durable=True)
            await queue.bind(exchange, "user_info.status")

            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        try:
                            data = json.loads(message.body)
                            print("THE DATA", data)
                            user_id = data.get("userId")

                            db = next(get_db())
                            user = await UserService.get_userInfo(user_id, db)
                            print("✅ User found:", user)

                            response_payload = {
                                "first_name": user.first_name,
                                "last_name": user.last_name,
                                "email": user.email,
                                "role": user.role,
                            }

                        except HTTPException as he:
                            # ถ้าไม่เจอ user ก็ส่ง response กลับไปแจ้งฝั่ง requester ด้วย
                            print(f"⚠️ User not found: {he.detail}")
                            response_payload = {
                                "error": "User not found",
                                "user_id": user_id,
                            }

                        except Exception as e:
                            print(f"❌ Unexpected error: {e}")
                            response_payload = {
                                "error": str(e),
                                "user_id": user_id,
                            }

                        # ✅ ไม่ว่าจะ error หรือไม่ ต้อง publish response กลับ (จะได้ไม่ requeue)
                        await exchange.publish(
                            aio_pika.Message(
                                body=json.dumps(response_payload).encode(),
                                correlation_id=message.correlation_id
                            ),
                            routing_key="user_info.response"
                        )
                        print(f"📤 Sent response for user {user_id}")

        except Exception as e:
            print(f"❌ Error in user service listener: {e}")
            await asyncio.sleep(5)
# ---------- RabbitMQ Listener End ----------


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

    # ✅ Start RabbitMQ listener in background
    asyncio.create_task(listen_rabbitmq())
    print("🚀 RabbitMQ listener started in background.")


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