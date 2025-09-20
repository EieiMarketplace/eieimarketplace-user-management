from sqlalchemy.orm import Session, joinedload
from . import models, auth

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).options(joinedload(models.User.role)).filter(models.User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_role_by_uuid(db: Session, user_uuid: str):
    """Get user role name by joining User and Role tables using user UUID."""
    user_with_role = db.query(models.User).options(joinedload(models.User.role)).filter(models.User.uuid == user_uuid).first()
    if user_with_role and user_with_role.role:
        return user_with_role.role.name
    return None

def get_user_by_uuid(db: Session, user_uuid: str):
    return db.query(models.User).filter(models.User.uuid == user_uuid).first()

def get_all_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, email, first_name, last_name, password, phone_number, role_name):
    role = db.query(models.Role).filter(models.Role.name == role_name).first()
    if not role:
        raise ValueError("Invalid role")
    hashed_pw = auth.hash_password(password)
    user = models.User(
        email=email, first_name=first_name, last_name=last_name,
        password=hashed_pw, phone_number=phone_number,
        role_id=role.id, uuid=auth.generate_uuid()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def blacklist_token(db: Session, token: str):
    blacklisted_token = models.BlacklistedToken(token=token)
    db.add(blacklisted_token)
    db.commit()
    return blacklisted_token

def is_token_blacklisted(db: Session, token: str):
    return db.query(models.BlacklistedToken).filter(models.BlacklistedToken.token == token).first() is not None


