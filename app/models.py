from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
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
    username = Column(String, unique=True, index=True)
    password = Column(String)
    phone_number = Column(String)
    role_id = Column(Integer, ForeignKey("role_table.id"))

    role = relationship("Role", back_populates="users")
