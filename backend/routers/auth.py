from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas.user import UserCreate,UserLogin, UserResponse
from backend.services import auth

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserResponse)
def register_user_route(user: UserCreate, db: Session = Depends(get_db)):
    try:
        return auth.register_user(db, user)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))



@router.post("/login", response_model=UserResponse)
def login_user_route(user: UserLogin, db: Session = Depends(get_db)):
    try:
        return auth.login_user(db, user)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
