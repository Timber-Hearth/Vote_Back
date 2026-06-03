from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from core.redis_client import get_redis
from models import Polls
from src.core.database import get_db
from src.exceptions.vote import VoteError
from src.schemas.vote import VoteRequest
from src.services.poll_service import ServiceGetPoll, DeletePollResultFromRedis
from src.services.vote_service import GetAnonymousId, NormalizeAnonymousId, ServiceVoteProcess
import os

vote_router = APIRouter()

@vote_router.post("/{token}")
def Vote(
    token: str,
    request: VoteRequest,
    response: Response,
    anonymous_id: str | None = Depends(GetAnonymousId),
    db: Session = Depends(get_db),
):
    poll_data = ServiceGetPoll(db, token)
    if not poll_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Poll not found")

    normalized_anonymous_id, is_new_cookie = NormalizeAnonymousId(anonymous_id)

    try:
        ServiceVoteProcess(db, poll_data, request.option_ids, normalized_anonymous_id)
    except VoteError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc

    if is_new_cookie:
        response.set_cookie(
            key="anonymous_id",
            value=str(normalized_anonymous_id),
            httponly=True,
            max_age=60 * 60 * 24 * 365,
        )
    DeletePollResultFromRedis(poll_data)
    return {"success": "vote done"}