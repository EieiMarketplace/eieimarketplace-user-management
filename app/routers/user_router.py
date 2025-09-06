from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import database, schemas, crud, auth, models

router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, user.email) or crud.get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Email or username already registered")
    new_user = crud.create_user(
        db, user.email, user.username, user.password, user.phone_number, user.role
    )
    return schemas.UserResponse(
        id=new_user.id,
        email=new_user.email,
        username=new_user.username,
        phone_number=new_user.phone_number,
        role=new_user.role.name
    )

@router.post("/login", response_model=schemas.Token)
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username)
    if not user or not auth.verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = auth.create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/users", response_model=list[schemas.UserResponse])
def get_all_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_all_users(db, skip=skip, limit=limit)
    return [
        schemas.UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            phone_number=user.phone_number,
            role=user.role.name
        ) for user in users
    ]

@router.get("/users/{user_id}", response_model=schemas.UserResponse)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return schemas.UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        phone_number=user.phone_number,
        role=user.role.name
    )

@router.post("/logout")
def logout():
    return {"message": "Logged out (client should discard token)"}