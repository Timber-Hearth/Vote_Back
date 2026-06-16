import os
from hashlib import sha256
import secrets
from typing import Annotated, Any

from fastapi import HTTPException
from fastapi.params import Depends
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone, UTC
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from redis_key import REDIS_KEY
from src.core.redis_client import get_redis
from src.core.util import IsDebugMode
from src.core.database import get_db
from src.models import User

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    # Keep local/dev behavior stable even when .env is missing.
    SECRET_KEY = "dev-only-secret-key-change-me"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
    auto_error=False,
)
MAX_BCRYPT_PASSWORD_BYTES = 72

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _ValidateBcryptPasswordLength(password: str) -> None:
    password_bytes = len(password.encode("utf-8"))
    if password_bytes > MAX_BCRYPT_PASSWORD_BYTES:
        raise ValueError(
            f"password must be {MAX_BCRYPT_PASSWORD_BYTES} bytes or less in UTF-8"
        )

def GetPasswordHash(password: str) -> str:
    _ValidateBcryptPasswordLength(password)
    return pwd_context.hash(password)

def VerifyPassword(password: str, _hash: str) -> bool:
    try:
        return pwd_context.verify(password, _hash)
    except ValueError:
        return False


def CreateAccessToken(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def VerifyAccessToken(token: str) -> dict[str, Any] | None:
    if not IsDebugMode():
        if IsTokenBlacklisted(token):
            return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        payload["exp"] = datetime.fromtimestamp(payload["exp"], timezone.utc)
        return payload
    except JWTError:
        return None

def GetCurrentUserFromJwt(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
):
    payload = VerifyAccessToken(token)
    if not payload:
        raise HTTPException(status_code=401, detail="invalid token")
    user = db.query(User).filter(User.id == payload["user_id"]).first()
    if not user:
        raise HTTPException(status_code=401, detail="user not found")
    return user


def GetCurrentUserFromJwtOptional(
    token: Annotated[str | None, Depends(oauth2_scheme_optional)],
    db: Annotated[Session, Depends(get_db)],
):
    if not token:
        return None

    payload = VerifyAccessToken(token)
    if not payload:
        return None

    user = db.query(User).filter(User.id == payload["user_id"]).first()
    return user

def _BlacklistKeyFromToken(token: str) -> str:
    token_hash = sha256(token.encode("utf-8")).hexdigest()
    key_prefix = REDIS_KEY["logout_blacklist"]
    return f"{key_prefix}{token_hash}"

def IsTokenBlacklisted(token: str) -> bool:
    redis = get_redis()
    key = _BlacklistKeyFromToken(token)
    try:
        return bool(redis.exists(key))
    except Exception:
        return True
    
def GenerateAnonymousId() -> str:
    annonymous_id = secrets.token_urlsafe(32)
    return annonymous_id