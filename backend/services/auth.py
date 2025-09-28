from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
import hashlib
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _pre_hash(password: str) -> str:
    """
    Pre-hash the password with SHA256 to avoid bcrypt 72-byte limit.
    Always encode before bcrypt.
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def hash_password(password: str) -> str:
    return pwd_context.hash(_pre_hash(password))

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(_pre_hash(password), hashed)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
