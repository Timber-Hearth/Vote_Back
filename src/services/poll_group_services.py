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