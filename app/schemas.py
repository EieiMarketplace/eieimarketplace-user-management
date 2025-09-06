from pydantic import BaseModel, EmailStr, validator, Field
import re

class UserCreate(BaseModel):
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=50, description="First name must be 1-50 characters")
    last_name: str = Field(..., min_length=1, max_length=50, description="Last name must be 1-50 characters")
    password: str = Field(..., min_length=8, max_length=100, description="Password must be 8-100 characters")
    phone_number: str = Field(..., min_length=10, max_length=15, description="Phone number must be 10-15 digits")
    role: str = Field(..., description="Role must be 'vendor' or 'organizer'")
    
    @validator('password')
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!+-_=@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        # Remove all non-digit characters
        phone_digits = re.sub(r'\D', '', v)
        if not re.match(r'^[0-9]{10,15}$', phone_digits):
            raise ValueError('Phone number must contain only digits and be 10-15 characters long')
        return phone_digits
    
    @validator('role')
    def validate_role(cls, v):
        allowed_roles = ['vendor', 'organizer']
        if v.lower() not in allowed_roles:
            raise ValueError(f'Role must be one of: {", ".join(allowed_roles)}')
        return v.lower()
    
    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty or only whitespace')
        if not re.match(r'^[a-zA-Z\s\-\.]+$', v.strip()):
            raise ValueError('Name can only contain letters, spaces, hyphens, and dots')
        return v.strip()

class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    phone_number: str
    role: str

    class Config:
        orm_mode = True

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str