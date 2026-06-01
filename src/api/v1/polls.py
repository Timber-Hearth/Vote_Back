from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import GetCurrentUserFromToken
from src.exceptions.poll import PollError, PollNotFoundError
from src.models import User
from src.schemas.poll import CreatePollRequest
from src.services.poll_service import ServiceCreatePoll, ServiceGetPoll, ServiceGetOptionsFromPollID

poll_router = APIRouter()

@poll_router.post("/create")
def CreatePoll(
    request: CreatePollRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(GetCurrentUserFromToken)],
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
