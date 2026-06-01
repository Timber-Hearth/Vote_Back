import uuid
from typing import List

from fastapi import Request
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Session

from src.models import Vote


def GetAnonymousId(request: Request):
    anonymous_id = request.cookies.get("anonymous_id")

    if anonymous_id:
        return anonymous_id

    return str(uuid.uuid4())



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