import uuid
from typing import List

from fastapi import Request
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Session

from src.models import Vote


def GetAnonymousId(request: Request):
    return request.cookies.get("anonymous_id")


def IsSingleUserTryVoteMultipleTime(anonymous_id : str, poll_id, db : Session):
    data = db.query(Vote).filter(Vote.poll_id == poll_id).filter(Vote.anonymous_id == anonymous_id).first()
    if data:
        return True
    return False

def IsThatOptionReallyExist(user_select : List[int], options : List):
    options_id = [x.id for x in options if x]
    for select in user_select:
        if select not in options_id:
            return False
    return True

def ServiceVoteProcess(db : Session, selected_options_id : int, poll_id : str, anonymous_id : str):
    vote_instance = Vote(
        poll_id = poll_id,
        option_id=selected_options_id,
        anonymous_id = anonymous_id
    )
    db.add(vote_instance)
    try:
        db.commit()
    except:
        db.rollback()
