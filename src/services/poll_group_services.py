from src.schemas.requests.PollGroup import Request_Create_PollGroup

from src.repositories.poll_group_repository import Repo_GetOptionsFromPollId, Repo_GetPollGroupData, Repo_GetPollDataFromPollGroupId

def BuildPollGroupDataForUser(db, token, data = None):
    group = data if data is not None else Repo_GetPollGroupData(db=db, token=token)
    if group is None:
        raise Exception("no data exist")
    polls = Repo_GetPollDataFromPollGroupId(db, group.id)
    result = []
    for poll in polls:
        options = Repo_GetOptionsFromPollId(db, poll.id)

        result.append({
            "id": poll.id,
            "title": poll.title,
            "description": poll.description,
            "allow_multiple_choice": poll.allow_multiple_choice,
            "options": [
                {
                    "option_text": opt.option_text,
                    "display_order": opt.display_order
                }
                for opt in options
            ]
        })
    return result

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