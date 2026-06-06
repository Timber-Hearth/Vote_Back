import os
import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.redis_client import get_redis
from src.repositories.poll_repository import GetPollByToken
from src.repositories.user_repository import GetPollListByUserId
from src.core.database import get_db
from src.core.security import GetCurrentUserFromJwt, GetCurrentUserFromJwtOptional
from src.exceptions.poll import PollError, PollNotFoundError
from src.models import User
from src.schemas.poll import CreatePollRequest
from src.services.poll_service import (
    BuildFinalPollData,
    PollPublicChecker,
    ServiceCreatePoll,
    ServiceGetOptionsFromPollID,
    ServiceGetPoll, SetPollClose, RemoveSinglePoll,
)

poll_router = APIRouter(tags=["polls"])

@poll_router.post(
    "/create",
    summary="투표 생성",
    description="로그인한 사용자가 새로운 투표를 생성합니다.",
    response_description="생성된 투표 정보",
    responses={
        401: {"description": "인증이 필요합니다."},
        400: {"description": "요청 데이터가 올바르지 않습니다."},
    },
)
def CreatePoll(
    request: CreatePollRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(GetCurrentUserFromJwt)],
):
    """새 투표를 생성합니다."""
    try:
        result = ServiceCreatePoll(db = db, owner_id = current_user.id, request = request)
    except PollError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
    return {"message" : "success", "data": result}

@poll_router.get(
    "/{token}",
    summary="투표 조회",
    description="토큰으로 투표 기본 정보와 옵션 목록을 조회합니다.",
    response_description="투표 정보 및 옵션 목록",
    responses={
        404: {"description": "투표를 찾을 수 없습니다."},
    },
)
def GetPoll(token: str, db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(GetCurrentUserFromJwt)]):
    """투표 기본 정보와 옵션을 조회하며, 가능하면 Redis 캐시를 사용합니다."""
    redis = get_redis()
    key_prefix = os.environ.get("REDIS_KEY_POLL", "poll:")
    try:
        cached_data = redis.get(f"{key_prefix}{token}")
    except Exception as exc:
        print(exc)
        cached_data = None
    if cached_data is not None:
        parsed = json.loads(cached_data)
        print("Redis - GetPollAndOptionsFromRedis")
        return parsed


    poll_data = ServiceGetPoll(db, token)
    poll_id = poll_data.owner_id
    is_my_poll = False
    if current_user is not None and poll_id == current_user.id:
            is_my_poll = True
    if not poll_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=PollNotFoundError().detail)
    options = ServiceGetOptionsFromPollID(db, poll_data.id)

    redis.set(
        f"{key_prefix}{token}",
        json.dumps({"data" : poll_data, "my_poll" : is_my_poll, "options" : options}, default=str),
        ex=60
    )
    
    return {"data" : poll_data, "options" : options}

@poll_router.get(
    "/{token}/result/list",
    summary="내 투표 목록 조회",
    description="현재 로그인한 사용자가 생성한 투표 목록을 조회합니다.",
    response_description="사용자 투표 목록",
    responses={
        401: {"description": "인증이 필요합니다."},
    },
)
def GetPollsByUserId(current_user: Annotated[User, Depends(GetCurrentUserFromJwt)], db: Annotated[Session, Depends(get_db)]):
    """현재 사용자 기준으로 투표 목록을 반환합니다."""
    return {"data" :GetPollListByUserId(db, current_user.id)}


@poll_router.get(
    "/{token}/result/detail",
    summary="투표 결과 상세 조회",
    description="QR 토큰으로 투표 결과 상세 데이터를 조회합니다.",
    response_description="투표 결과 상세",
    responses={
        403: {"description": "결과를 조회할 권한이 없습니다."},
        404: {"description": "투표를 찾을 수 없습니다."},
    },
) # token은 qr토큰이다
def GetPollResultDetail(
    token: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User | None, Depends(GetCurrentUserFromJwtOptional)],
):
    poll = GetPollByToken(db, token)
    if not poll:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Poll not found")

    if PollPublicChecker(poll, current_user) is False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission to view this poll")
    
    key_prefix = os.environ.get("REDIS_KEY_POLL_RESULT", "poll_result:")
    key = f"{key_prefix}{poll.id}"
    redis = get_redis()
    
    cached_data = redis.get(key)
    if cached_data is not None:
        print("Redis - GetDataFromRedis")
        return {"data": json.loads(cached_data)}
    
    result = BuildFinalPollData(db, poll)
    
    try:
        redis.set(
            key,
            json.dumps(result, default=str),
            ex=60
        )
    except Exception as exc:
        print(exc)
    
    return {"data": result}

@poll_router.post(
    "/{token}/close",
    summary="투표 종료",
    description="투표 소유자가 투표를 종료 상태로 변경합니다.",
    response_description="투표 종료 결과",
    responses={
        403: {"description": "투표를 종료할 권한이 없습니다."},
        404: {"description": "투표를 찾을 수 없습니다."},
    },
)
def ClosePoll(
    token: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(GetCurrentUserFromJwt)],
):
    """투표를 종료하고 관련 캐시를 정리합니다."""
    poll = GetPollByToken(db, token)
    if not poll:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Poll not found")

    if poll.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission to close this poll")

    val = SetPollClose(db, poll)
    if val is False:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    
    try:
        redis = get_redis()
        key = f"{os.environ.get('REDIS_KEY_POLL', 'poll:')}{token}"
        redis.delete(key)
    except Exception as exc:
        print(exc)
    
    return {"message" : "success"}

@poll_router.delete(
    "/{token}/remove",
    summary="투표 삭제",
    description="투표 소유자가 투표를 삭제합니다.",
    response_description="투표 삭제 결과",
    responses={
        403: {"description": "투표를 삭제할 권한이 없습니다."},
        404: {"description": "투표를 찾을 수 없습니다."},
    },
)
def RemovePoll(
    token: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(GetCurrentUserFromJwt)],
):
    """투표를 삭제하고 관련 캐시를 정리합니다."""
    poll = GetPollByToken(db, token)
    if not poll:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Poll not found")

    if poll.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission to remove this poll")

    val = RemoveSinglePoll(db, poll)
    if val is False:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

    try:
        redis = get_redis()
        key = f"{os.environ.get('REDIS_KEY_POLL', 'poll:')}{token}"
        redis.delete(key)
    except Exception as exc:
        print(exc)
    
    return {"message" : "success"}
