import os
import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from src.core.redis_client import get_redis
from src.repositories.poll_repository import GetPollByToken, GetPollListByUserId
from src.core.database import get_db
from src.core.security import GetCurrentUserFromJwt, GetCurrentUserFromJwtOptional
from src.exceptions.poll import PollError, PollNotFoundError
from src.models import User
from src.schemas.requests.poll import CreatePollRequest
from src.schemas.responses.poll import (
    CreatePollResponse,
    PollDetailResponse,
    PollListResponse,
    PollMessageResponse,
    PollResultDetailResponse,
)
from src.services.poll_service import (
    BuildFinalPollData,
    PollPublicChecker,
    ServiceCreatePoll,
    ServiceGetOptionsFromPollID,
    ServiceGetPoll, SetPollClose, RemoveSinglePoll,
)

poll_router = APIRouter(tags=["polls"])


def _ToPublicPollData(poll_obj: object, qr_token: str) -> dict:
    data = jsonable_encoder(poll_obj)
    if isinstance(data, dict):
        data.pop("id", None)
        data["qr_token"] = qr_token
    return data


def _NormalizeCreatePollResponse(payload: dict) -> dict:
    result = dict(payload)
    result.pop("poll_id", None)
    token = result.get("token")
    if token is not None:
        result["qr_token"] = token
    return result


def _NormalizePollResultDetail(payload: dict, qr_token: str) -> dict:
    result = dict(payload)
    poll_data = result.get("poll_data")
    if isinstance(poll_data, dict):
        poll_data = dict(poll_data)
        poll_data.pop("id", None)
        poll_data["qr_token"] = qr_token
        result["poll_data"] = poll_data
    return result

@poll_router.post(
    "/create",
    response_model=CreatePollResponse,
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
    try:
        result = ServiceCreatePoll(db = db, owner_id = current_user.id, request = request)
    except PollError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
    return {"message" : "success", "data": _NormalizeCreatePollResponse(result)}

@poll_router.get(
    "/{token}",
    response_model=PollDetailResponse,
    summary="투표 조회",
    description="토큰으로 투표 기본 정보와 옵션 목록을 조회합니다.",
    response_description="투표 정보 및 옵션 목록",
    responses={
        404: {"description": "투표를 찾을 수 없습니다."},
    },
)
def GetPoll(token: str, db: Annotated[Session, Depends(get_db)]):
    redis = get_redis()
    key_prefix = os.environ.get("REDIS_KEY_POLL", "poll:")
    try:
        cached_data = redis.get(f"{key_prefix}{token}")
    except Exception as exc:
        print(exc)
        cached_data = None
    if cached_data is not None:
        parsed = json.loads(cached_data)
        if isinstance(parsed, dict) and isinstance(parsed.get("data"), dict):
            parsed["data"] = _ToPublicPollData(parsed["data"], token)
        print("Redis - GetPollAndOptionsFromRedis")
        return parsed

    poll_data = ServiceGetPoll(db, token)
    if not poll_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=PollNotFoundError().detail)
    options = ServiceGetOptionsFromPollID(db, poll_data.id)
    response_payload = {"data": _ToPublicPollData(poll_data, token), "options": options}

    redis.set(
        f"{key_prefix}{token}",
        json.dumps(response_payload, default=str),
        ex=60
    )
    
    return response_payload

@poll_router.get(
    "/result/list",
    response_model=PollListResponse,
    summary="내 투표 목록 조회",
    description="현재 로그인한 사용자가 생성한 투표 목록을 조회합니다.",
    response_description="사용자 투표 목록",
    responses={
        401: {"description": "인증이 필요합니다."},
    },
)
def GetPollsByUserId(current_user: Annotated[User, Depends(GetCurrentUserFromJwt)], db: Annotated[Session, Depends(get_db)]):
    key_prefix = os.environ.get("REDIS_KEY_POLL_LIST")
    key = f"{key_prefix}{current_user.id}"
    redis = get_redis()

    cached_data = redis.get(key)
    if cached_data is not None:
        print("Redis - GetDataFromRedis")
        return {"data": json.loads(cached_data)}
    
    data = GetPollListByUserId(db, current_user.id)
    try:
        redis.set(key, json.dumps(data, default=str), ex=60)
    except Exception:
        pass
    return {"data": data}


@poll_router.get(
    "/{token}/result/detail",
    response_model=PollResultDetailResponse,
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
        cached_result = json.loads(cached_data)
        if isinstance(cached_result, dict):
            cached_result = _NormalizePollResultDetail(cached_result, token)
        return {"data": cached_result}
    
    if current_user is None:
        result = BuildFinalPollData(db, poll)
    else:
        result = BuildFinalPollData(db, poll, current_user)
    result = _NormalizePollResultDetail(result, token)
    
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
    response_model=PollMessageResponse,
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
    response_model=PollMessageResponse,
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
