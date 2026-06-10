import os
import json
import secrets
from datetime import datetime
from email import message
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from models import QrTokens, PollGroup
from src.schemas.requests.PollGroup import CreatePollGroupRequest
from src.schemas.responses.poll_group import CreatePollDataResponse

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
    try:
        poll_group_id = GetLastPollGroupId()
        for single_poll in request.polls:
            ServiceCreatePoll(db=db, request=single_poll, poll_group_id=poll_group_id)


        token = secrets.token_urlsafe(16)
        qr_token = QrTokens(
            poll_group_id=GetLastPollGroupId(),
            tokens=token,
        )
        db.add(qr_token)

        poll_group = PollGroup(
            title=request.title,
            owner_id=current_user.id,
            description=request.description,
            is_public_result=request.is_public_result,
            is_closed=False,
            created_at= datetime,
            expire_at=datetime,
            delete_after_hours=request.delete_after_hours
        )
        db.add(poll_group)
        db.refresh()
    except Exception as e:
        print(e)
        return {"title": request.title, "message": "false"}

    return {"title":request.title,"message":"true"}



# 나중에 pollgroupid 마지막 값 리턴하게 바꿔
def GetLastPollGroupId() -> int:
    return 0