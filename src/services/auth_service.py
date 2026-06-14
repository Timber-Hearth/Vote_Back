import os
from datetime import UTC, datetime, timedelta
import uuid

from fastapi import Request
from sqlalchemy.orm import Session

from src.core.redis_client import get_redis
from src.exceptions.auth import InvalidCredentialsError, UserAlreadyExistsError, LoginAttemptLimitExceededError
from src.core.security import GetPasswordHash, VerifyPassword
from src.repositories.user_repository import CreateUser, GetUserByLoginID


def ServiceSignUp(db: Session, login_id : str, password : str, expire_at: datetime = None):
    exist_user = GetUserByLoginID(db, login_id)
    if exist_user:
        raise UserAlreadyExistsError()

    hash_password = GetPasswordHash(password)
    return CreateUser(db, login_id, hash_password, expire_at)

def SetExpireAtDate(request):
    return request.expire_at or (datetime.now(UTC) + timedelta(days=7))

def ServiceLogin(db: Session, login_id: str, password: str):
    redis = get_redis()
    redis_key = f"{os.environ.get('REDIS_KEY_LOGIN_LIMIT', 'login_limit:')}{login_id}"    
    current_attempts = redis.incr(redis_key)
    if current_attempts == 1:
        redis.expire(redis_key, 30)
    if current_attempts >= 5:
        raise LoginAttemptLimitExceededError()
    
    exist_user = GetUserByLoginID(db, login_id)
    if exist_user and VerifyPassword(password, exist_user.password_hash):
        redis.delete(redis_key)
        return exist_user

    raise InvalidCredentialsError()


def GetAnonymousId(request: Request) -> str | None:
    return request.cookies.get("anonymous_id")


def NormalizeAnonymousId(anonymous_id: str | None) -> tuple[uuid.UUID, bool]:
    if anonymous_id is None:
        return uuid.uuid4(), True

    try:
        return uuid.UUID(str(anonymous_id)), False
    except (TypeError, ValueError, AttributeError):
        return uuid.uuid4(), True
    
    
def GetClientIp(request: Request) -> str:
    if os.environ.get("DEBUG_MODE") == "1":
        return request.client.host
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()

    return request.client.host