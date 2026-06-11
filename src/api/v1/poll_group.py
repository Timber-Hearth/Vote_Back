from core.security import GetCurrentUserFromJwt
from fastapi import APIRouter, Depends, HTTPException
from httpx import request
from sqlalchemy.orm import Session

from src.services.auth_service import GetAnonymousId
from src.services.poll_group_services import BuildPollGroupDataForUser, VerifyPollGroupData
from src.models import PollGroup
from src.repositories.poll_group_repository import Repo_CreatePollGroup, Repo_GetPollGroupData
from src.core.database import get_db

from src.schemas.requests.PollGroup import Get_PollGroupRequest, Request_Create_PollGroup
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
        404: {"description": "투표를 찾을 수 없습니다."},
        500 : {"description": "서버 에러"}
    }
)
def Get_PollData(request: Get_PollGroupRequest, db: Session = Depends(get_db)):
    try:
        data = Repo_GetPollGroupData(db=db, token=request.token)
        if data is None:
            raise HTTPException(status_code=404, detail="투표를 찾을 수 없습니다.")
        return { "data" : BuildPollGroupDataForUser(db, request.token), "message" : "success" }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@poll_group_router.get(
    path="/get_tokens",
    summary="로그인한 유저가 만든 투표들의 토큰들 가져오기",
    description="로그인한 유저가 만든 투표들의 토큰들 가져오기",
    response_description="로그인한 유저가 만든 투표들의 토큰들 가져오기",
    responses={
        404: {"description": "투표를 찾을 수 없습니다."},
        500 : {"description": "서버 에러"}
    }
)
def Get_PollGroupTokens(db: Session = Depends(get_db), current_user = Depends(GetCurrentUserFromJwt)):
    try:
        poll_groups = db.query(PollGroup).filter(PollGroup.owner_id == current_user.id).all()
        tokens = [pg.token for pg in poll_groups]
        return {"tokens": tokens, "message": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@poll_group_router.post(
    path="/create_poll_group",
    summary="투표 그룹 생성",
    description="투표 그룹 생성",
    response_description="투표 그룹 생성 결과",
    responses={
        200: {"description": "투표 그룹이 성공적으로 생성되었습니다."},
        500: {"description": "서버 에러"},
    }
)
def Create_PollGroup(request: Request_Create_PollGroup, db: Session = Depends(get_db), current_user = Depends(GetCurrentUserFromJwt)):
    try:
        if request is None:
            raise HTTPException(status_code=400, detail="잘못된 요청입니다.")
        if VerifyPollGroupData(request) and current_user is not None:
            # TODO : 이곳에 qr 생성 로직 추가
            if Repo_CreatePollGroup(db, current_user.id, request):
                return {"message": "success"}
            else:
                raise HTTPException(status_code=500, detail="투표 그룹 생성에 실패했습니다.")
        else:
            raise HTTPException(status_code=400, detail="유효하지 않은 투표 그룹 데이터입니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))