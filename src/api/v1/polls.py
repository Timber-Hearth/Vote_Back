from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import GetCurrentUserFromToken
from models import User
from schemas.poll import CreatePollRequest
from services.poll_service import ServiceCreatePoll

poll_router = APIRouter()

@poll_router.post("/create")
def CreatePoll(request : CreatePollRequest, db : Session = Depends(get_db), current_user: User = Depends(GetCurrentUserFromToken)):
    poll = ServiceCreatePoll(db = db, owner_id = current_user.id, request = request)
    return {"message" : "success", "poll_id" : str(poll.id)}
