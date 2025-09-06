from fastapi import FastAPI
from .database import Base, engine
from .models import Role
from .routers import user_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Eiei Marketplace User Management")

# init default roles
from sqlalchemy.orm import Session
db = Session(bind=engine)
if not db.query(Role).all():
    db.add_all([Role(name="vendor"), Role(name="organizer")])
    db.commit()
db.close()

app.include_router(user_router.router, prefix="/users", tags=["Users"])
