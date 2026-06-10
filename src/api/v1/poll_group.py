from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from src.repositories.poll_group_repository import Repo_GetPollGroupData
from src.core.database import get_db

from src.services.vote_service import GetAnonymousId
from src.schemas.requests.PollGroup import Get_PollGroupRequest
from src.schemas.responses.poll_group import Response_PollGroup_Token

poll_group_router = APIRouter(tags=["poll_group"])


# 이건말야, 투표의 루트로 하자고
@poll_group_router.get(
    path="/{token}",
    response_model=Response_PollGroup_Token,
    summary="토큰을 통해 공개 가능한 투표 데이터 끌어오기",
    description="qr_token을 집어넣으면 공개 가능한 대상 데이터들을 리턴한다. 미로그인 사용자들이 볼 수 있는 데이터들.",
    response_description="투표 데이터 가져오기",
    responses={
        404: {"description": "투표를 찾을 수 없습니다."}
    }
)
def Get_PollData(
    request: Get_PollGroupRequest,
    response: Response,
    anonymous_id: str | None = Depends(GetAnonymousId),
    db: Session = Depends(get_db)
):
    Repo_GetPollGroupData(db=db, token=request.token)