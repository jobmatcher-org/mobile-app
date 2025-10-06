from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas.user import UserCreate, UserResponse
from backend.services import auth

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    return auth.register_user(db, user)

@router.post("/login")
def login_user(user: UserCreate, db: Session = Depends(get_db)):
    return auth.login_user(db, user)
