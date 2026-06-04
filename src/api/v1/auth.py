import os
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from src.core.redis_client import get_redis
from src.core.security import ALGORITHM, SECRET_KEY, CreateAccessToken, oauth2_scheme
from src.core.util import StrConvertToHashForRedis
from src.core.database import get_db
from src.exceptions.auth import AuthError, LoginAttemptLimitExceededError
from src.schemas.auth import LoginRequest, SignUpRequest
from src.services.auth_service import ServiceLogin, ServiceSignUp

auth_router = APIRouter(tags=["auth"])

@auth_router.post(
    "/login",
    summary="로그인",
    description="아이디/비밀번호로 로그인하고 액세스 토큰을 발급합니다.",
    response_description="액세스 토큰 정보",
    responses={
        401: {"description": "아이디 또는 비밀번호가 올바르지 않습니다."},
        429: {"description": "로그인 시도 횟수를 초과했습니다. 잠시 후 다시 시도하세요."},
    },
)
def Login(request: LoginRequest, db: Annotated[Session, Depends(get_db)]):
    """로그인 요청을 처리하고 Bearer 토큰을 반환합니다."""
    try:
        user = ServiceLogin(db, request.login_id, request.password)
    except AuthError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
    except LoginAttemptLimitExceededError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail)

    token = CreateAccessToken(
        {
            "sub" : user.login_id,
            "user_id" : user.id
        }
    )
    
    return {"access_token" : token, "token_type" : "bearer"}

@auth_router.post(
    "/signup",
    summary="회원가입",
    description="새 사용자 계정을 생성합니다.",
    response_description="회원가입 결과",
    responses={
        409: {"description": "이미 존재하는 아이디입니다."},
    },
)
def SignUp(request: SignUpRequest, db: Annotated[Session, Depends(get_db)]):
    """회원가입 요청을 처리하고 성공 메시지를 반환합니다."""
    try:
        ServiceSignUp(db, request.login_id, request.password)
    except AuthError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc

    return {"message" : "success"}
    
@auth_router.post(
    "/logout",
    summary="로그아웃",
    description="현재 Bearer 토큰을 블랙리스트에 등록해 즉시 무효화합니다.",
    response_description="로그아웃 결과",
    responses={
        401: {"description": "토큰이 유효하지 않습니다."},
        500: {"description": "로그아웃 처리 중 서버 오류가 발생했습니다."},
    },
)
def Logout(token: Annotated[str, Depends(oauth2_scheme)]):
    """토큰 만료 시간까지 Redis 블랙리스트에 토큰을 저장합니다."""
    redis = get_redis()
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp_ts = int(payload["exp"])
        now_ts = int(datetime.now(UTC).timestamp())
        ttl = exp_ts - now_ts
        if ttl <= 0:
            return {"message" : "success"}
        token_hash = StrConvertToHashForRedis(token)
        key_prefix = os.environ.get("REDIS_KEY_LOGOUT_BLACKLIST", "token_blacklist:")
        key = f"{key_prefix}{token_hash}"
        redis.setex(key, ttl, "1")
        return {"message" : "success"}
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="invalid token") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="logout failed") from exc