import datetime
from typing import Annotated
from hashlib import sha256

from fastapi import APIRouter, Depends, HTTPException
from jose import jwt, JWTError
from sentry_sdk.envelope import PayloadRef
from sentry_sdk.integrations.redis import redis
from sqlalchemy.orm import Session

from core.redis_client import get_redis
from core.security import SECRET_KEY, ALGORITHM
from src.core.database import get_db
from src.exceptions.auth import AuthError
from src.core.security import CreateAccessToken, oauth2_scheme
from src.schemas.auth import LoginRequest, SignUpRequest
from src.services.auth_service import ServiceLogin, ServiceSignUp

auth_router = APIRouter()

@auth_router.post("/login")
def Login(request: LoginRequest, db: Annotated[Session, Depends(get_db)]):
    try:
        user = ServiceLogin(db, request.login_id, request.password)
    except AuthError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc

    token = CreateAccessToken(
        {
            "sub" : user.login_id,
            "user_id" : user.id
        }
    )
    return {"access_token" : token, "token_type" : "bearer"}

@auth_router.post("/signup")
def SignUp(request: SignUpRequest, db: Annotated[Session, Depends(get_db)]):
    try:
        ServiceSignUp(db, request.login_id, request.password)
    except AuthError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc

    return {"message" : "success"}
    
@auth_router.post("/logout")
def Logout(token: Annotated[str, Depends(oauth2_scheme)]):
    redis = get_redis()
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp_ts = int(payload["exp"])
        now_ts = int(datetime.now(datetime.UTC).timestamp())
        ttl = exp_ts - now_ts
        if ttl <= 0:
            return {"message" : "success"}
        token_hash = sha256(token.encode("utf-8")).hexdigest()
        key = f"sv:auth:blacklist:{token_hash}"
        redis.setex(key, ttl, "1")
        return {"message" : "success"}
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="invalid token") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="logout failed") from exc