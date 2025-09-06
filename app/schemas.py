from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    phone_number: str
    role: str  # vendor | organizer

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    phone_number: str
    role: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str