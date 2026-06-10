import os
import json
import secrets
from datetime import datetime
from email import message
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from models import QrTokens, PollGroup
from src.repositories.poll_group_repository import Repo_CreatePollGroup
from src.repositories.qr_token_repository import Repo_CreateQrToken
from src.schemas.requests.PollGroup import CreatePollGroupRequest
from src.schemas.responses.poll_group import CreatePollDataResponse

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from src.core.redis_client import get_redis
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
poll_group_router = APIRouter(tags=["/poll_group"])

@poll_group_router.post(
    path="/create",
    response_model=CreatePollDataResponse,
    summary="투표 그룹 생성",
    description="로그인한 사용자가 투표그룹 생성",
    response_description="생성된 투표 토큰과 메시지",
    responses={
        401: {"description": "인증이 필요합니다."},
        400: {"description": "요청 데이터가 올바르지 않습니다."},
    },
)
def CreatePollGroup(
    request: CreatePollGroupRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(GetCurrentUserFromJwt)]
):
    poll_group = Repo_CreatePollGroup(db=db, request=request, current_user=current_user)
    for single_poll in request.polls:
        ServiceCreatePoll(db=db, request=single_poll, poll_group_id=poll_group.id)
    qr_token = Repo_CreateQrToken(db=db, poll_group=poll_group)
    # TODO : 레디스에 저장해두자
    return {"title":request.title,"message":"true", "token": qr_token.tokens}


# TODO : 여기서 레디스에 있는거 불러오기, 없다면 ㄴpoll_service 에서 끌어올것
def GetPollGroup():
    pass
