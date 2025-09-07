from fastapi import FastAPI
from .database import Base, engine
from .models import Role
from .routers import user_router
from fastapi.middleware.cors import CORSMiddleware
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Eiei Marketplace User Management")
list = ["http://localhost:5000",
        "http://localhost:8000",
        "http://localhost:3000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=list,       
    allow_credentials=True,
    allow_methods=["*"],          # GET, POST, PUT, DELETE, OPTIONS
    allow_headers=["*"],          # Authorization, Content-Type, etc.
)
# init default roles
from sqlalchemy.orm import Session
db = Session(bind=engine)
if not db.query(Role).all():
    db.add_all([Role(name="vendor"), Role(name="organizer")])
    db.commit()
db.close()

app.include_router(user_router.router, prefix="/users", tags=["Users"])
