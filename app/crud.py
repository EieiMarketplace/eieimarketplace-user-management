from typing import List
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

def get_users_by_uuids(db: Session, user_uuids: List[str]) -> List[dict]:
    """Get multiple users by their UUIDs"""
    users = db.query(models.User).filter(models.User.uuid.in_(user_uuids)).all()
    
    result = []
    for user in users:
        result.append({
            "vendorId": user.uuid,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "role": "vendor",
        })
    
    # Add "Unknown" for missing users
    found_ids = {user.uuid for user in users}
    for user_id in user_uuids:
        if user_id not in found_ids:
            result.append({
                "vendorId": user_id,
                "first_name": "Unknown",
                "last_name": "",
                "email": "",
                "role": "",
            })
    
    return result

def get_all_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, email, first_name, last_name, password, phone_number, role_name):
    role = db.query(models.Role).filter(models.Role.name == role_name).first()
    if not role:
        raise ValueError("Invalid role")
    salt = auth.generate_salt()
    hashed_pw = auth.hash_password(password, salt)

    user = models.User(
        email=email, first_name=first_name, last_name=last_name,
        password=hashed_pw, phone_number=phone_number,
        role_id=role.id, uuid=auth.generate_uuid(),
        salt=salt
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

def edit_user(db: Session, user_uuid: str, email: str = None, first_name: str = None, last_name: str = None, password: str = None, phone_number: str = None):
    user = get_user_by_uuid(db, user_uuid)
    if not user:
        raise ValueError("User not found")
    if email:
        if email != user.email and get_user_by_email(db, email):
            raise ValueError("Email already in use")
        user.email = email
    if first_name:
        user.first_name = first_name
    if last_name:
        user.last_name = last_name
    if phone_number:
        user.phone_number = phone_number
    db.commit()
    db.refresh(user)
    return user

def edit_password(db: Session, user_uuid: str, new_password: str):
    user = get_user_by_uuid(db, user_uuid)
    if not user:
        raise ValueError("User not found")
    new_salt = auth.generate_salt()
    user.password = auth.hash_password(new_password, new_salt)
    user.salt = new_salt
    db.commit()
    db.refresh(user)
    return user