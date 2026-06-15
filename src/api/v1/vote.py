import json
import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from fastapi.encoders import jsonable_encoder

from src.core.database import get_db
from src.core.redis_client import get_redis
from src.core.redis_client import get_redis
from src.repositories.poll_group_repository import Repo_GetPollGroupData
from src.schemas.requests.vote import VoteRequest
from src.services.auth_service import GetAnonymousId, NormalizeAnonymousId
from typing import Annotated
from sqlalchemy.orm import Session

from src.services.vote_services import VoteProcess

vote_router = APIRouter(tags=["vote"])


@vote_router.post(
    "/{token}",
    summary="투표하기",
    description="투표하기",
    response_description="투표 결과",
    responses={
        401: {"description": "토큰이 유효하지 않습니다."},
        404: {"description": "투표할 항목이 존재하지 않습니다."},
        500: {"description": "투표 처리 중 서버 오류가 발생했습니다."},
    },
)
def Vote(
    token: str,
    request: VoteRequest,
    response: Response,
    annonymous_id: Annotated[str, Depends(GetAnonymousId)],
    db: Annotated[Session, Depends(get_db)],
):
    """투표 요청을 처리하고 투표 결과를 반환합니다."""
    redis = get_redis()
    redis_key = os.environ.get("REDIS_KEY_GET_POLL_GROUP") + token
    cache = redis.get(redis_key)
    if cache is None:
        poll_data = Repo_GetPollGroupData(db=db, token=token)
        if poll_data is None:
            raise HTTPException(status_code=404, detail="투표할 항목이 존재하지 않습니다.")
        redis.set(redis_key, json.dumps(jsonable_encoder(poll_data)), ex=60 * 5)
    else:
        poll_data = json.loads(cache)
    try:
        normalized_annonymou_id, new_cookie = NormalizeAnonymousId(annonymous_id)
        if new_cookie:
            response.set_cookie(
                key="anonymous_id", 
                value=normalized_annonymou_id,
                httponly=True,
                max_age=60*60*24*365*1,
            )

        VoteProcess(db, poll_data, normalized_annonymou_id, request.options)
        return {"message": "투표가 성공적으로 처리되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))