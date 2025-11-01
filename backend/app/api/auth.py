"""
Authentication API Routes
User signup, login, and profile management
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.dependencies import get_current_active_user
from app.core.config import settings
from app.models import User, Wallet
from app.schemas import UserCreate, UserLogin, User as UserSchema, Token, UserUpdate

router = APIRouter()


@router.post("/signup", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user account

    Creates a new user with:
    - Hashed password
    - Default skill level (beginner)
    - Default theme (professional)
    - Associated wallet

    Returns:
        Created user object
    """
    # Check if user already exists
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password
    )

    db.add(new_user)
    await db.flush()  # Flush to get user.id

    # Create wallet for user
    wallet = Wallet(user_id=new_user.id)
    db.add(wallet)

    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Login with email and password

    Uses OAuth2 password flow.
    Returns JWT access token on success.

    Args:
        form_data: OAuth2 form with username (email) and password

    Returns:
        Access token for authenticated requests
    """
    # Get user by email
    result = await db.execute(
        select(User).where(User.email == form_data.username)
    )
    user = result.scalar_one_or_none()

    # Verify credentials
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last login
    user.last_login = datetime.utcnow()
    await db.commit()

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login/json", response_model=Token)
async def login_json(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Login with JSON body (alternative to OAuth2 form)

    Accepts JSON with email and password.
    Returns JWT access token on success.

    Args:
        credentials: Email and password in JSON

    Returns:
        Access token for authenticated requests
    """
    # Get user by email
    result = await db.execute(
        select(User).where(User.email == credentials.email)
    )
    user = result.scalar_one_or_none()

    # Verify credentials
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last login
    user.last_login = datetime.utcnow()
    await db.commit()

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserSchema)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user information

    Requires valid JWT token in Authorization header.

    Returns:
        Current user profile
    """
    return current_user


@router.patch("/me", response_model=UserSchema)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update current user profile

    Allows updating:
    - Skill level (beginner/intermediate/expert)
    - Theme preference

    Args:
        user_update: Fields to update
        current_user: Authenticated user

    Returns:
        Updated user profile
    """
    if user_update.skill_level is not None:
        current_user.skill_level = user_update.skill_level

    if user_update.theme_preference is not None:
        current_user.theme_preference = user_update.theme_preference

    await db.commit()
    await db.refresh(current_user)

    return current_user
