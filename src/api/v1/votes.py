from datetime import UTC, datetime
from fastapi import Request
from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm.session import Session

from services.poll_service import ServiceGetOptionsFromPollID
from src.services.vote_service import IsSingleUserTryVoteMultipleTime, GetAnonymousId, IsThatOptionReallyExist
from src.services.poll_service import ServiceGetPoll
from src.core.database import get_db
from schemas.vote import VoteRequest

vote_router = APIRouter()

@vote_router.post("/{token}")
def Vote(token : str, request : VoteRequest, anonymous_id = Depends(GetAnonymousId), db : Session = Depends(get_db)):
    poll_data = ServiceGetPoll(db, token)
    if not poll_data:
        return {"error": "Poll not found"}
    if poll_data.is_closed:
        return {"error" : "already closed poll"}
    if IsSingleUserTryVoteMultipleTime(anonymous_id, poll_data.id, db):
        return {"error" : "you can vote only once"}
    if poll_data.expire_at and poll_data.expire_at < datetime.now(UTC):
        return {"error": "poll expired"}
    options = ServiceGetOptionsFromPollID(db, poll_data.id)
    if not options:
        return {"error" : "this poll has no option"}
    user_selected_options = request.option_ids
    if len(user_selected_options) == 0:
        return {"error" : "user didn't select option"}
    if len(user_selected_options) > 1 and poll_data.allow_multiple_choice == False:
        return {"error" : "this poll can't select multiple option"}
    if not IsThatOptionReallyExist(user_selected_options, options):
        return {"error" : "that option not exist in db"}

    pass