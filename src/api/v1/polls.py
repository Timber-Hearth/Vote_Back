from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pygments.lexers import data
from sqlalchemy.orm import Session

from repositories.poll_repository import GetPollByToken
from repositories.user_repository import GetPollListByUserId
from repositories.vote_repository import CalculateVoteCount
from src.core.database import get_db
from src.core.security import GetCurrentUserFromJwt
from src.exceptions.poll import PollError, PollNotFoundError
from src.models import User
from src.schemas.poll import CreatePollRequest
from src.services.poll_service import ServiceCreatePoll, ServiceGetPoll, ServiceGetOptionsFromPollID

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
def GetPollResultDetail(token: str, db: Annotated[Session, Depends(get_db)], current_user: Annotated[User | None, Depends(GetCurrentUserFromJwt)]):
    poll = GetPollByToken(db, token)
    if not poll:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Poll not found")

    if not poll.is_public_result:
        if not current_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login required")
        if poll.owner_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can't see this poll")

    data = CalculateVoteCount(db, poll.id)
    options = ServiceGetOptionsFromPollID(db, poll.id)
    result = {
        "poll_data" : poll,
        "options" :[{
            "option_id": opt.id,
            "option_text": opt.option_text,
            "count": data.get(opt.id, 0),
        }
        for opt in options
    ]}
    return {"data": result}