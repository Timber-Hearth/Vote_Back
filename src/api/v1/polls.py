from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

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
    ServiceGetPoll,
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
    poll_data = ServiceGetPoll(db, token)
    if not poll_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=PollNotFoundError().detail)
    options = ServiceGetOptionsFromPollID(db, poll_data.id)
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
    result = BuildFinalPollData(db, poll)
    return {"data": result}