from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    password: str
    phone_number: str
    role: str  # vendor | organizer

class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    phone_number: str
    role: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str