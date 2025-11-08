from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from backend import models, schemas
from backend.services import crud
from backend.database import get_db
from backend.models.user import User
from datetime import datetime, timedelta
from jose import jwt
# ---------------------------
# Password utilities
# ---------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



SECRET_KEY = "your_secret_key_here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def hash_password(password: str) -> str:
    """Hash plain password."""
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    """Verify plain password against hashed password."""
    return pwd_context.verify(password, hashed)

# ---------------------------
# User registration
# ---------------------------
def register_user(db: Session, user: schemas.user.UserCreate):
    """Register a new user with hashed password."""
    existing = crud.get_user_by_email(db, user.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    hashed_pw = hash_password(user.password)
    return crud.create_user(db, user, hashed_pw)

# ---------------------------
# User login
# ---------------------------
def login_user(db: Session, user: schemas.user.UserLogin):
    """Authenticate user and verify password."""
    db_user = crud.get_user_by_email(db, user.email)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Temporary: return user object for testing UI connection
    return db_user

# ---------------------------
# Temporary current user
# ---------------------------
def get_current_user(db: Session = Depends(get_db)):
    """
    Temporary function to simulate an authenticated user.
    In real auth, you'd decode a JWT and fetch the actual user.
    """
    user = db.query(User).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No user found in database. Please register one first."
        )
    return user
