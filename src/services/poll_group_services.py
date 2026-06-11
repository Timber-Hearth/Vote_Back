from schemas.requests.PollGroup import Request_Create_PollGroup

from src.repositories.poll_group_repository import Repo_GetOptionsFromPollId, Repo_GetPollGroupData, Repo_GetPollDataFromPollGroupId


def BuildPollGroupDataForUser(db, token):
    data = Repo_GetPollGroupData(db=db, token=token)
    if data is None:
        print("no data exist")
        # TODO : 에러 작성
    polls = Repo_GetPollDataFromPollGroupId(db, data.id)
    poll_data_list = []
    for item in polls:
        poll_id = item.id
        Repo_GetOptionsFromPollId(db, poll_id)
        if poll_id is None:
            print("no data exist")
            # TODO : 에러 작성
        poll_data_list.append({
            "title" : item.title,
            "description" : item.description,
            "allow_multiple_choice" : item.allow_multiple_choice,
            "options" : Repo_GetOptionsFromPollId(db, poll_id)
        })



    open_data = {
        "token" : data.qr_token,
        "title" : data.title,
        "description" : data.description,
        "is_closed" : data.is_closed,
        "created_at" : data.created_at,
        "delete_after_hours" : data.delete_after_hours,
        "is_public_result" : data.is_public_result,
        "expire_at" : data.expire_at,
        "poll" : poll_data_list
    }

    return open_data

def VerifyPollGroupData(request: Request_Create_PollGroup):
    if request is None:
        raise ValueError("잘못된 요청입니다.")
    if not request.title:
        raise ValueError("제목은 필수입니다.")
    if not request.poll_data_list or len(request.poll_data_list) == 0:
        raise ValueError("투표 데이터는 최소 하나 이상이어야 합니다.")
    for poll_data in request.poll_data_list:
        if not poll_data.title:
            raise ValueError("각 투표의 제목은 필수입니다.")
        if not poll_data.options or len(poll_data.options) == 0:
            raise ValueError("각 투표는 최소 하나 이상의 옵션이 필요합니다.")
        for option in poll_data.options:
            if not option.option_text:
                raise ValueError("각 옵션의 텍스트는 필수입니다.")
    return True