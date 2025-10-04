from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import HTTPAuthorizationCredentials
from .. import database, schemas, crud, auth
from fastapi import Depends, HTTPException, status
router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = crud.create_user(
        db, user.email, user.first_name, user.last_name, user.password, user.phone_number, user.role
    )
    return schemas.UserResponse(
        id=new_user.uuid,
        email=new_user.email,
        first_name=new_user.first_name,
        last_name=new_user.last_name,
        phone_number=new_user.phone_number,
        role=new_user.role.name
    )

@router.post("/login", response_model=schemas.LoginResponse)
def login(login_data: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, login_data.email)
    if not user or not auth.verify_password(login_data.password, user.password, user.salt):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Get role name from relationship
    role_name = user.role.name if user.role else "unknown"
    
    # Include role in token payload for authorization
    token = auth.create_access_token({"sub": user.uuid, "role": role_name})
    
    return {
        "access_token": token,
        "id": user.uuid,
        "role": role_name
    }


# @router.get("/users", response_model=list[schemas.UserResponse])
# def get_all_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     users = crud.get_all_users(db, skip=skip, limit=limit)
#     return [
#         schemas.UserResponse(
#             id=user.uuid,
#             email=user.email,
#             first_name=user.first_name,
#             last_name=user.last_name,
#             phone_number=user.phone_number,
#             role=user.role.name
#         ) for user in users
#     ]

# #TODO change user_id to uuid
@router.get("/{user_id}", response_model=schemas.UserResponse)
def get_user_by_uuid(user_id: str, credentials: HTTPAuthorizationCredentials = Depends(auth.security), db: Session = Depends(get_db)):
    """Get current user info based on the provided JWT token."""
    token = credentials.credentials

    # Check if token is blacklisted
    if crud.is_token_blacklisted(db, token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = crud.get_user_by_uuid(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return schemas.UserResponse(
        id=user.uuid,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        phone_number=user.phone_number,
        role=user.role.name
    )

# Get current user info
@router.get("/info", response_model=schemas.UserResponse)
def get_user_info(credentials: HTTPAuthorizationCredentials = Depends(auth.security), db: Session = Depends(get_db)):
    """Get current user info based on the provided JWT token."""
    token = credentials.credentials
    
    # Check if token is blacklisted
    if crud.is_token_blacklisted(db, token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    uuid = auth.verify_token(token, db)
    user = crud.get_user_by_uuid(db, uuid)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return schemas.UserResponse(
        id=user.uuid,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        phone_number=user.phone_number,
        role=user.role.name
    )

# Edit current user info
@router.put("/info", response_model=schemas.UserResponse)
def edit_user_info(
    update_data: schemas.EditUserRequest,
    credentials: HTTPAuthorizationCredentials = Depends(auth.security), 
    db: Session = Depends(get_db)
):
    """Edit current user info based on the provided JWT token."""
    token = credentials.credentials
    
    # Check if token is blacklisted
    if crud.is_token_blacklisted(db, token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    uuid = auth.verify_token(token, db)
    user = crud.get_user_by_uuid(db, uuid)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        # Update user info
        updated_user = crud.edit_user(
            db, uuid,
            email=update_data.email,
            first_name=update_data.first_name,
            last_name=update_data.last_name,
            phone_number=update_data.phone_number
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return schemas.UserResponse(
        id=updated_user.uuid,
        email=updated_user.email,
        first_name=updated_user.first_name,
        last_name=updated_user.last_name,
        phone_number=updated_user.phone_number,
        role=updated_user.role.name
    )

@router.put("/password")
def change_password(
    password_data: schemas.ChangePasswordRequest,
    credentials: HTTPAuthorizationCredentials = Depends(auth.security), 
    db: Session = Depends(get_db)
):
    """Change current user's password based on the provided JWT token."""
    token = credentials.credentials
    
    # Check if token is blacklisted
    if crud.is_token_blacklisted(db, token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    

    uuid = auth.verify_token(token, db)
    user = crud.get_user_by_uuid(db, uuid)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    crud.edit_password(db, uuid, password_data.new_password)

    return {"message": "Password changed successfully"}


@router.post("/verify", response_model=schemas.VerifyResponse)
def verify_user(
    verify_request: schemas.VerifyRequest,
    credentials: HTTPAuthorizationCredentials = Depends(auth.security), 
    db: Session = Depends(get_db)
):
    """Verify if a user has the required role authorization."""
    token = credentials.credentials
    uuid = verify_request.uuid
    required_role = verify_request.required_role
    
    # Use the is_authorized function which handles all the verification logic
    is_authorized = auth.is_authorized(db, token, required_role, uuid)
    
    return schemas.VerifyResponse(
        uuid=uuid,
        verify=is_authorized
    )

@router.post("/logout")
def logout(credentials: HTTPAuthorizationCredentials = Depends(auth.security), db: Session = Depends(get_db)):
    token = credentials.credentials
    
    # Add token to blacklist
    crud.blacklist_token(db, token)
    
    return {"message": "Successfully logged out"}