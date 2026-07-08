import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from fastapi.encoders import jsonable_encoder

from redis_key import REDIS_KEY
from src.core.database import get_db
from src.core.redis_client import get_redis
from src.core.redis_client import get_redis
from src.repositories.poll_group_repository import Repo_GetPollGroupData, Repo_GetPollOptionData
from src.schemas.requests.vote import VoteRequest
from src.services.auth_service import GetAnonymousId, NormalizeAnonymousId
from typing import Annotated
from sqlalchemy.orm import Session

from src.exceptions.vote import VoteError
from src.services.vote_services import VoteProcess

vote_router = APIRouter(tags=["vote"])


@vote_router.post(
    "/vote",
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
    request: VoteRequest,
    response: Response,
    annonymous_id: Annotated[str, Depends(GetAnonymousId)],
    db: Annotated[Session, Depends(get_db)],
):
    # TODO : 옵션 가져올떄도 레디스를 거치게 한다 아직은 말고
    """투표 요청을 처리하고 투표 결과를 반환합니다."""
    redis = get_redis()
    redis_key = REDIS_KEY["get_poll_group"] + request.vote_qr
    full_option_data = Repo_GetPollOptionData(db=db, token=request.vote_qr)

    if full_option_data is None or len(full_option_data) == 0:
        raise HTTPException(status_code=404, detail="투표할 항목이 존재하지 않습니다.")
    cache = redis.get(redis_key)
    if cache is None:
        poll_data = Repo_GetPollGroupData(db=db, token=request.vote_qr)
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
        for poll_id, single_vote in request.options.items():
            VoteProcess(db, request.vote_qr, normalized_annonymou_id, poll_id, single_vote)
        db.commit()
        return {"message": "투표가 성공적으로 처리되었습니다."}
    except VoteError as e:
        db.rollback()
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))