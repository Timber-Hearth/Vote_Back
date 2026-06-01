import uuid
from datetime import UTC, datetime
from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm.session import Session
from fastapi import Response

from services.poll_service import ServiceGetOptionsFromPollID
from src.services.vote_service import IsSingleUserTryVoteMultipleTime, GetAnonymousId, IsThatOptionReallyExist, ServiceVoteProcess
from src.services.poll_service import ServiceGetPoll
from src.core.database import get_db
from schemas.vote import VoteRequest

vote_router = APIRouter()

@vote_router.post("/{token}")
def Vote(token : str, request : VoteRequest, response : Response, anonymous_id = Depends(GetAnonymousId), db : Session = Depends(get_db)):
    poll_data = ServiceGetPoll(db, token)
    if not poll_data:
        return {"error": "Poll not found"}
    if anonymous_id is None:
        anonymous_id = str(uuid.uuid4())
        response.set_cookie(
            key = "anonymous_id",
            value = anonymous_id,
            httponly = True,
            max_age=60 * 60 * 24 * 365,
        )
    if poll_data.expire_at and poll_data.expire_at < datetime.now(UTC):
        return {"error": "poll expired"}
    if poll_data.is_closed:
        return {"error" : "already closed poll"}
    if poll_data.allow_multiple_choice == False and IsSingleUserTryVoteMultipleTime(anonymous_id, poll_data.id, db):
        return {"error" : "you can vote only once"}
    options = ServiceGetOptionsFromPollID(db, poll_data.id)
    if not options:
        return {"error" : "this poll has no option"}
    user_selected_options = request.option_ids
    if len(user_selected_options) > 1 and poll_data.allow_multiple_choice == False:
        return {"error" : "this poll can't select multiple option"}
    if not IsThatOptionReallyExist(user_selected_options, options):
        return {"error" : "that option not exist in db"}

    for select in user_selected_options:
        ServiceVoteProcess(db, select, poll_data.id, anonymous_id)
    return {"success" : "vote done"}
