import os
from typing import Any

from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone, UTC
from jose import jwt, JWTError

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
SECRET_KEY = os.environ.get("SECRET_KEY")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
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
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        payload["exp"] = datetime.fromtimestamp(payload["exp"], timezone.utc)
        return payload
    except JWTError:
        return None
