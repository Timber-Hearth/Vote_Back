from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import GetCurrentUserFromToken
from models import User
from schemas.poll import CreatePollRequest
from services.poll_service import ServiceCreatePoll, ServiceGetPoll

poll_router = APIRouter()

@poll_router.post("/create")
def CreatePoll(request : CreatePollRequest, db : Session = Depends(get_db), current_user: User = Depends(GetCurrentUserFromToken)):
    result = ServiceCreatePoll(db = db, owner_id = current_user.id, request = request)
    return {"message" : "success", "data": result}

@poll_router.get("/{token}")
def GetPoll(token : str, db : Session = Depends(get_db)):
    poll_data = ServiceGetPoll(db, token)
    if not poll_data:
        return {"error": "Poll not found"}
    return {"data": poll_data} # TODO : 옵션 데이터도 들고 올수 있게 해야 할까?
