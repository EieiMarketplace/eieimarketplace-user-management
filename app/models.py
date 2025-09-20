from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Role(Base):
    __tablename__ = "role_table"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)

    users = relationship("User", back_populates="role")

class User(Base):
    __tablename__ = "user_table"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    uuid = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    password = Column(String)
    salt = Column(String)
    phone_number = Column(String)
    role_id = Column(Integer, ForeignKey("role_table.id"))
    role = relationship("Role", back_populates="users")

class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    blacklisted_at = Column(DateTime, default=datetime.utcnow)
