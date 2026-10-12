from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from datetime import datetime, timedelta, timezone
import jwt
from dotenv import load_dotenv
from pwdlib import PasswordHash
from sqlalchemy.orm import Session
from database import get_db
from models import User

password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)

load_dotenv()

def create_access_token(subject: str) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=30)
    payload = {"sub": subject, "exp": expires}
    return jwt.encode(
        payload, os.environ["JWT_SECRET_KEY"], algorithm="HS256"
    )

bearer_scheme = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    try:
        payload = jwt.decode(
            credentials.credentials,
            os.environ["JWT_SECRET_KEY"],
            algorithms=["HS256"],
        )
        user_id = int(payload["sub"])
    except (jwt.InvalidTokenError, ValueError, KeyError):
        raise HTTPException(401, "Invalid or expired token")
    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise HTTPException(401, "Invalid or inactive user")
    return user