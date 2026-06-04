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

poll_router = APIRouter()

@poll_router.post("/create")
def CreatePoll(
    request: CreatePollRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(GetCurrentUserFromJwt)],
):
    try:
        result = ServiceCreatePoll(db = db, owner_id = current_user.id, request = request)
    except PollError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
    return {"message" : "success", "data": result}

@poll_router.get("/{token}")
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
        print("Redis - GetPollAndOptionsFromRedis")
        return {"data": parsed["poll"], "options": parsed["options"]}

    poll_data = ServiceGetPoll(db, token)
    if not poll_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=PollNotFoundError().detail)
    options = ServiceGetOptionsFromPollID(db, poll_data.id)

    redis.set(
        f"{key_prefix}{token}",
        json.dumps({"data" : poll_data, "options" : options}, default=str),
        ex=60
    )
    
    return {"data" : poll_data, "options" : options}

@poll_router.get("/{token}/result/list") # TODO : 테스트 필요해
def GetPollsByUserId(current_user: Annotated[User, Depends(GetCurrentUserFromJwt)], db: Annotated[Session, Depends(get_db)]):
    return {"data" :GetPollListByUserId(db, current_user.id)}


@poll_router.get("/{token}/result/detail") # token은 qr토큰이다
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

@poll_router.post("/{token}/close")
def ClosePoll(
    token: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(GetCurrentUserFromJwt)],
):
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

@poll_router.delete("/{token}/remove")
def RemovePoll(
    token: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(GetCurrentUserFromJwt)],
):
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
