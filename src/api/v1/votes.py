from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from src.core.redis_client import get_redis
from src.core.database import get_db
from src.exceptions.vote import VoteError
from src.schemas.requests.vote import VoteRequest
from src.schemas.responses.vote import VoteResponse
from src.services.poll_service import ServiceGetPoll, DeletePollResultFromRedis
from src.services.vote_service import GetAnonymousId, NormalizeAnonymousId, ServiceVoteProcess

vote_router = APIRouter(tags=["votes"])


# TODO : 이곳 전부 다시 작업할것
@vote_router.post(
    "/{token}",
    response_model=VoteResponse,
    summary="투표하기",
    description="QR 토큰에 해당하는 투표에 옵션을 제출합니다.",
    response_description="투표 처리 결과",
    responses={
        404: {"description": "투표를 찾을 수 없습니다."},
        409: {"description": "이미 투표했거나 유효하지 않은 투표 요청입니다."},
        429: {"description": "중복 제출이 감지되어 잠시 차단되었습니다."},
    },
)
def Vote(
    token: str,
    request: VoteRequest,
    response: Response,
    anonymous_id: str | None = Depends(GetAnonymousId),
    db: Session = Depends(get_db),
):
    """익명 식별자 기준으로 투표를 처리하고 결과 캐시를 무효화합니다."""
    poll_data = ServiceGetPoll(db, token)
    if not poll_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Poll not found")
    normalized_anonymous_id, is_new_cookie = NormalizeAnonymousId(anonymous_id)

    redis = get_redis()
    lock_key = f"vote:lock:{poll_data.id}:{normalized_anonymous_id}"
    lock_acquired = False

    try:
        acquired = redis.set(lock_key, "1", nx=True, ex=3)
        if not acquired:
            raise HTTPException(status_code=429, detail="Too many requests. Please try again.")
        lock_acquired = True
    except HTTPException:
        raise
    except Exception:
        pass
    try:
        ServiceVoteProcess(db, poll_data, request.option_ids, normalized_anonymous_id)
    except VoteError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
    finally:
        if lock_acquired:
            try:
                redis.delete(lock_key)
            except Exception:
                pass

    if is_new_cookie:
        response.set_cookie(
            key="anonymous_id",
            value=str(normalized_anonymous_id),
            httponly=True,
            max_age=60 * 60 * 24 * 365,
        )
    DeletePollResultFromRedis(poll_data)
    return {"success": "vote done"}