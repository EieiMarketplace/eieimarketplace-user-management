from sqlalchemy.orm import Session
from . import models, auth

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, email, username, password, phone_number, role_name):
    role = db.query(models.Role).filter(models.Role.name == role_name).first()
    if not role:
        raise ValueError("Invalid role")
    hashed_pw = auth.hash_password(password)
    user = models.User(
        email=email, username=username,
        password=hashed_pw, phone_number=phone_number,
        role_id=role.id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user