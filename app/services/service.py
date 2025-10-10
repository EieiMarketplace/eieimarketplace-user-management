from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException

from .. import database2, schemas, crud

def get_db():
    db = database2.SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserService:
    @staticmethod
    async def get_userInfo(user_id: str, db: Session) -> schemas.UserResponse:
        # synchronous query ยังคงอยู่
        user = crud.get_user_by_uuid(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return schemas.UserResponse(
            id=user.uuid,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone_number=user.phone_number,
            role='vendor'
        )
