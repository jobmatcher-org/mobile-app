from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas.user import UserCreate, UserLogin, UserResponse
from backend.services import auth
from backend.services.auth import create_access_token  # make sure you have this function

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserResponse)
def register_user_route(user: UserCreate, db: Session = Depends(get_db)):
    try:
        return auth.register_user(db, user)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/login")
def login_user_route(user: UserLogin, db: Session = Depends(get_db)):
    # ✅ Verify credentials using your existing auth logic
    db_user = auth.login_user(db, user)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # ✅ Create JWT token containing user_id (required by get_current_user)
    access_token = create_access_token(data={"user_id": db_user.id})

    # ✅ Return token + user info
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(db_user)
    }