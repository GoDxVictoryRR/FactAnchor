from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from ...db.session import get_async_session
from ...db.models import User
from ...auth.jwt import verify_password, create_access_token, hash_password

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    email: str

class SignupRequest(BaseModel):
    email: EmailStr
    password: str

def validate_password(password: str):
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    if not any(char.isdigit() for char in password):
        raise HTTPException(status_code=400, detail="Password must contain at least one number")
    if not any(not char.isalnum() for char in password):
        raise HTTPException(status_code=400, detail="Password must contain at least one special character")

@router.post("/signup", response_model=LoginResponse)
async def signup(
    req: SignupRequest,
    session: AsyncSession = Depends(get_async_session)
):
    """ Create a new user and return JWT. """
    validate_password(req.password)
    
    # Check if user exists
    stmt = select(User).where(User.email == req.email)
    result = await session.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User already exists")
    
    user = User(
        email=req.email,
        hashed_password=hash_password(req.password),
        is_active=True
    )
    session.add(user)
    await session.commit()
    
    access_token = create_access_token(user_id=str(user.id))
    return LoginResponse(access_token=access_token, email=user.email)

@router.post("/login", response_model=LoginResponse)
async def login(
    req: LoginRequest,
    session: AsyncSession = Depends(get_async_session)
):
    """ Authenticate user and return JWT. """
    stmt = select(User).where(User.email == req.email)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is inactive"
        )
        
    access_token = create_access_token(user_id=str(user.id))
    return LoginResponse(access_token=access_token, email=user.email)
