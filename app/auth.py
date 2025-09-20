from passlib.context import CryptContext
from datetime import datetime, timedelta, UTC
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from . import database, crud
import uuid

SECRET_KEY = "supersecret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(password: str, salt: str):
    return pwd_context.hash(password + salt)

def generate_salt():
    # randomly generate a salt value 32
    return str(uuid.uuid4())

def verify_password(plain, hashed, salt):
    return pwd_context.verify(plain + salt, hashed)

def generate_uuid():
    return str(uuid.uuid4())

def create_access_token(data: dict, expires_delta: int = None):
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=expires_delta or ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str, db: Session):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        uuid: str = payload.get("sub")
        if uuid is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return uuid
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
def verify_authorization(token: str, db: Session):
    """Extract UUID and role from JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        uuid: str = payload.get("sub")
        role: str = payload.get("role")        
        if uuid is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return uuid, role
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    
    # Check if token is blacklisted
    if crud.is_token_blacklisted(db, token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    uuid = verify_token(token, db)
    user = crud.get_user_by_uuid(db, uuid)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# Authorization functions
def is_authorized(db: Session, token: str, required_role: str, uuid: str = None):
    """
    Check if the token holder is authorized with the required role.
    
    Args:
        db: Database session
        token: JWT token
        required_role: The role required for authorization
        uuid: Optional UUID to verify token belongs to specific user
        
    Returns:
        bool: True if authorized, False otherwise
    """
    try:
        token_uuid, token_role = verify_authorization(token, db)

        # Check if UUID matches (if provided)
        if uuid and token_uuid != uuid:
            return False
            
        # Check if role matches requirement
        if token_role != required_role:
            return False
            
        return True
    except Exception:
        return False
