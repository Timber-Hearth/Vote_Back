import json
import os
from typing import List

from redis_key import REDIS_KEY
from src.core.redis_client import get_redis
from src.core.security import GetCurrentUserFromJwt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.services.poll_group_services import BuildPollGroupDataForUser, VerifyPollGroupData
from src.models import PollGroup
from src.repositories.poll_group_repository import Repo_AddDeleteTime, Repo_CreatePollGroup, Repo_GetPollGroupByToken, Repo_GetPollGroupData, Repo_GetPollSettingsByToken, Repo_OwnerCheckerByToken, Repo_OwnerCheker, Repo_SetPublic, Repo_EditExpireTime
from src.core.database import get_db

from src.schemas.requests.PollGroup import ChangeTimeRequest, Request_Create_PollGroup, Request_Token, Request_Token, SetPublicRequest
from src.schemas.responses.poll_group import Response_PollGroup_Token

poll_group_router = APIRouter(tags=["poll_group"])


# 이건말야, 투표의 루트로 하자고
@poll_group_router.get(
    path="/token/{token}",
    response_model=Response_PollGroup_Token,
    summary="토큰을 통해 공개 가능한 투표 데이터 끌어오기",
    description="qr_token을 집어넣으면 공개 가능한 대상 데이터들을 리턴한다. 미로그인 사용자들이 볼 수 있는 데이터들.",
    response_description="투표 데이터 가져오기",
    responses={
        404: {"description": "투표를 찾을 수 없습니다."},
        500 : {"description": "서버 에러"}
    }
)
def Get_PollData(token: str, db: Session = Depends(get_db)):
    try:
        redis = get_redis()
        cache = redis.get(REDIS_KEY["get_poll_group"] + token)
        if cache is not None:
            return {"data": json.loads(cache), "message": "success"}
        data = Repo_GetPollGroupData(db=db, token=token)
        if data is None:
            raise HTTPException(status_code=404, detail="투표를 찾을 수 없습니다.")
        return_data = BuildPollGroupDataForUser(db, token, data)
        redis.set(REDIS_KEY["get_poll_group"] + token, json.dumps(return_data), ex=60 * 5)
        return { "data" : return_data, "message" : token}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@poll_group_router.get(
    path="/all_my_polls",
    summary="로그인한 유저가 만든 투표의 모든 정보 가져오기",
    description="로그인한 유저가 만든 투표의 모든 정보 가져오기",
    response_description="로그인한 유저가 만든 투표의 모든 정보 가져오기",
    responses={
        404: {"description": "투표를 찾을 수 없습니다."},
        500 : {"description": "서버 에러"}
    }
)
def Get_PollGroups(db: Session = Depends(get_db), current_user = Depends(GetCurrentUserFromJwt)):
    try:
        if current_user is None:
            raise HTTPException(status_code=401, detail="인증이 필요합니다.")
        poll_groups: List[PollGroup] = db.query(PollGroup).filter(PollGroup.owner_id == current_user.id).all()
        return {"poll_groups": poll_groups, "message": "success"}
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
        if current_user is None:
            raise HTTPException(status_code=401, detail="인증이 필요합니다.")
        poll_groups: List[PollGroup] = db.query(PollGroup).filter(PollGroup.owner_id == current_user.id).all()
        tokens = [pg.qr_token for pg in poll_groups]
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
            if Repo_CreatePollGroup(db, current_user.id, request):
                return {"message": "success"}
            else:
                raise HTTPException(status_code=500, detail="투표 그룹 생성에 실패했습니다.")
        else:
            raise HTTPException(status_code=400, detail="유효하지 않은 투표 그룹 데이터입니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@poll_group_router.post(
    path="/close_poll_group",
    summary="투표 그룹 닫기",
    description="투표 그룹 닫기",
    response_description="투표 그룹 닫기 결과",
    responses={
        200: {"description": "투표 그룹이 성공적으로 닫혔습니다."},
        403: {"description": "권한이 없습니다."},
        404: {"description": "투표 그룹을 찾을 수 없습니다."},
        500: {"description": "서버 에러"},
    }
)
def Close_PollGroup(request: Request_Token, db: Session = Depends(get_db), current_user = Depends(GetCurrentUserFromJwt)):
    try:
        if Repo_OwnerCheckerByToken(db, current_user.id, request.token) is not True:
            raise HTTPException(status_code=401, detail="인증이 필요하거나 권한 부족.")
        poll_group = Repo_GetPollGroupByToken(request.token, db)
        if poll_group is None:
            raise HTTPException(status_code=404, detail="투표 그룹을 찾을 수 없습니다.")
        poll_group.is_closed = True
        db.commit()
        return {"message": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@poll_group_router.post(
    path="/open_poll_group",
    summary="투표 그룹 열기",
    description="투표 그룹 열기",
    response_description="투표 그룹 열기 결과, 그러니까 is_closed가 false로 바뀌는 결과",
    responses={
        200: {"description": "투표 그룹이 성공적으로 열렸습니다."},
        403: {"description": "권한이 없습니다."},
        404: {"description": "투표 그룹을 찾을 수 없습니다."},
        500: {"description": "서버 에러"},
    }
)
def Open_PollGroup(request: Request_Token, db: Session = Depends(get_db), current_user = Depends(GetCurrentUserFromJwt)):
    try:
        if Repo_OwnerCheckerByToken(db, current_user.id, request.token) is not True:
            raise HTTPException(status_code=401, detail="인증이 필요하거나 권한 부족.")
        poll_group = Repo_GetPollGroupByToken(request.token, db)
        if poll_group is None:
            raise HTTPException(status_code=404, detail="투표 그룹을 찾을 수 없습니다.")
        poll_group.is_closed = False
        db.commit()
        return {"message": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@poll_group_router.post(
    path="/change_delete_time/",
    summary="투표 그룹 삭제 시간 변경",
    description="투표 그룹 삭제 시간 변경",
    response_description="투표 그룹 삭제 시간 변경 결과",
    responses={
        200: {"description": "투표 그룹 삭제 시간이 성공적으로 변경되었습니다."},
        403: {"description": "권한이 없습니다."},
        404: {"description": "투표 그룹을 찾을 수 없습니다."},
        500: {"description": "서버 에러"},
    }
)
def AddDeleteTime(request: ChangeTimeRequest, db: Session = Depends(get_db), current_user = Depends(GetCurrentUserFromJwt)):
    try:
        if Repo_OwnerCheckerByToken(db, current_user.id, request.token) is not True:
            raise HTTPException(status_code=401, detail="인증이 필요하거나 권한 부족.")
        poll_group = Repo_GetPollGroupByToken(request.token, db)
        if poll_group is None:
            raise HTTPException(status_code=404, detail="투표 그룹을 찾을 수 없습니다.")
        if Repo_AddDeleteTime(db, request.token, request.add_hours):
            return {"message": "success"}
        else:
            raise HTTPException(status_code=500, detail="투표 그룹 삭제 시간 변경에 실패했습니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@poll_group_router.post(
    path="/get_poll_settings",
    summary="투표 그룹 설정 가져오기",
    description="투표 그룹 설정 가져오기",
    response_description="투표 그룹 설정 가져오기 결과",
    responses={
        200: {"description": "투표 그룹 설정이 성공적으로 가져왔습니다."},
        403: {"description": "권한이 없습니다."},
        404: {"description": "투표 그룹을 찾을 수 없습니다."},
        500: {"description": "서버 에러"},
    }
)
def GetPollSettings(request: Request_Token, db: Session = Depends(get_db), current_user = Depends(GetCurrentUserFromJwt)):
    try:
        if Repo_OwnerCheckerByToken(db, current_user.id, request.token) is not True:
            raise HTTPException(status_code=401, detail="인증이 필요하거나 권한 부족.")
        poll_settings = Repo_GetPollSettingsByToken(request.token, db)
        if poll_settings is None:
            raise HTTPException(status_code=404, detail="투표 그룹을 찾을 수 없습니다.")
        return {"poll_settings": poll_settings, "message": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@poll_group_router.post(
    path="/edit_expire_time/",
    summary="투표 그룹 만료 시간 변경",
    description="투표 그룹 만료 시간 변경",
    response_description="투표 그룹 만료 시간 변경 결과",
    responses={
        200: {"description": "투표 그룹 만료 시간이 성공적으로 변경되었습니다."},
        403: {"description": "권한이 없습니다."},
        404: {"description": "투표 그룹을 찾을 수 없습니다."},
        500: {"description": "서버 에러"},
    }
)
def EditExpireTime(request: ChangeTimeRequest, db: Session = Depends(get_db), current_user = Depends(GetCurrentUserFromJwt)):
    try:
        if Repo_OwnerCheckerByToken(db, current_user.id, request.token) is not True:
            raise HTTPException(status_code=401, detail="인증이 필요하거나 권한 부족.")
        poll_group = Repo_GetPollGroupByToken(request.token, db)
        if poll_group is None:
            raise HTTPException(status_code=404, detail="투표 그룹을 찾을 수 없습니다.")
        if Repo_EditExpireTime(db, request.token, request.add_hours):
            return {"message": "success"}
        else:
            raise HTTPException(status_code=500, detail="투표 그룹 만료 시간 변경에 실패했습니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@poll_group_router.post(
    path="/set_public",
    summary="투표 그룹 공개 여부 설정",
    description="투표 그룹 공개 여부 설정",
    response_description="투표 그룹 공개 여부 설정 결과",
    responses={
        200: {"description": "투표 그룹 공개 여부가 성공적으로 설정되었습니다."},
        403: {"description": "권한이 없습니다."},
        404: {"description": "투표 그룹을 찾을 수 없습니다."},
        500: {"description": "서버 에러"},
    }
)
def SetPublic(request: SetPublicRequest, db: Session = Depends(get_db), current_user = Depends(GetCurrentUserFromJwt)):
    if Repo_OwnerCheckerByToken(db, current_user.id, request.token) is not True:
        raise HTTPException(status_code=401, detail="인증이 필요하거나 권한 부족.")
    poll_group = Repo_GetPollGroupByToken(request.token, db)
    if poll_group is None:
        raise HTTPException(status_code=404, detail="투표 그룹을 찾을 수 없습니다.")
    if not Repo_SetPublic(db, request.token, request.is_public):
        raise HTTPException(status_code=500, detail="투표 그룹 공개 여부 설정에 실패했습니다.")
    return {"message": "success"}